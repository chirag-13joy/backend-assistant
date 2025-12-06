from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import json
from datetime import datetime

from app.logic.scheduler import Topic


# =========================
# DATA STRUCTURES
# =========================

@dataclass
class TopicPerformance:
    topic_name: str
    attempts: int = 0
    correct: int = 0
    last_difficulty: str = "medium"   # "easy" | "medium" | "hard"
    last_updated_iso: str = ""        # ISO string


def _topic_perf_to_dict(perf: TopicPerformance) -> Dict[str, Any]:
    return asdict(perf)


def _topic_perf_from_dict(data: Dict[str, Any]) -> TopicPerformance:
    return TopicPerformance(
        topic_name=str(data.get("topic_name", "")),
        attempts=int(data.get("attempts", 0)),
        correct=int(data.get("correct", 0)),
        last_difficulty=str(data.get("last_difficulty", "medium")),
        last_updated_iso=str(data.get("last_updated_iso", "")),
    )


# =========================
# HELPERS
# =========================

def _find_topic(topics: List[Topic], topic_name: str) -> Optional[Topic]:
    target = (topic_name or "").strip().lower()
    for topic in topics:
        if topic.name.strip().lower() == target:
            return topic
    return None


def _now_iso() -> str:
    # UTC ISO like 2025-11-27T12:34:56Z
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _get_or_create_topic_perf(
    performance_store: Dict[str, Dict[str, Any]],
    topic_name: str,
) -> TopicPerformance:
    if topic_name in performance_store:
        return _topic_perf_from_dict(performance_store[topic_name])

    perf = TopicPerformance(
        topic_name=topic_name,
        attempts=0,
        correct=0,
        last_difficulty="medium",
        last_updated_iso=_now_iso(),
    )
    performance_store[topic_name] = _topic_perf_to_dict(perf)
    return perf


practice_system_prompt = """
You are a strict practice question generator and answer checker.

Rules:
- Focus on high-quality, exam-relevant questions.
- Be direct and honest in feedback.
- Avoid motivational fluff; focus on what the student did right/wrong.
- Always return VALID JSON ONLY. No text, no markdown, no commentary outside JSON.
""".strip()


def _wrap_llm_request(
    action: str,
    user_prompt: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    req: Dict[str, Any] = {
        "messages": [
            {"role": "system", "content": practice_system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "metadata": {"practice_action": action},
    }

    if metadata:
        req["metadata"].update(metadata)

    return req


# =========================
# ADAPTIVE DIFFICULTY
# =========================

def suggest_difficulty_from_performance(
    performance_store: Dict[str, Dict[str, Any]],
    topic_name: str,
) -> str:
    raw = performance_store.get(topic_name)
    if not raw:
        return "medium"

    perf = _topic_perf_from_dict(raw)

    if perf.attempts <= 0:
        return "medium"

    accuracy = perf.correct / perf.attempts

    if accuracy >= 0.8:
        return "hard"
    elif accuracy <= 0.4:
        return "easy"
    else:
        return "medium"


# =========================
# GENERATE PRACTICE QUESTIONS
# =========================

def generate_practice_questions_request(
    topics: List[Topic],
    performance_store: Dict[str, Dict[str, Any]],
    topic_name: str,
    difficulty: str,
    count: int,
) -> Dict[str, Any]:
    topic = _find_topic(topics, topic_name)
    if topic is None:
        return {"error": True, "reason": f"topic_not_found: {topic_name}"}

    difficulty = (difficulty or "auto").strip().lower()
    if difficulty == "auto":
        difficulty = suggest_difficulty_from_performance(
            performance_store=performance_store,
            topic_name=topic_name,
        )

    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "medium"

    topic_context = {
        "name": topic.name,
        "subject_name": topic.subject_name,
        "difficulty": getattr(topic.difficulty, "value", str(topic.difficulty)),
        "weight": getattr(topic.weight, "value", str(topic.weight)),
        "weakness": getattr(topic.weakness, "value", str(topic.weakness)),
        "progress": float(topic.progress),
        "base_hours": float(topic.base_hours),
    }

    topic_json_str = json.dumps(topic_context, ensure_ascii=False)

    count = max(1, int(count))

    user_prompt = f"""
You are in PRACTICE QUESTION GENERATION MODE.

Topic JSON:
{topic_json_str}

Target difficulty: "{difficulty}".
You must generate EXACTLY {count} questions.
The "questions" array MUST contain exactly {count} items — no more, no fewer.

Return ONLY a JSON object with this exact shape:

{{
  "kind": "practice_questions",
  "topic_name": string,
  "subject_name": string,
  "difficulty": string,           // "easy" | "medium" | "hard"
  "questions": [
    {{
      "id": string,
      "question_type": string,    // "mcq" | "short_answer" | "concept" | "application"
      "prompt": string,
      "options": [string],        // empty if not MCQ
      "correct_answer": any,      // index or text depending on type
      "explanation": string,
      "metadata": object          // optional extra info
    }}
  ]
}}

Constraints:
- Questions must be exam-relevant for this topic.
- Use clear, unambiguous language.
- Prefer a mix of MCQ and short-answer, unless the topic clearly demands one style.
- Do NOT include any text outside this JSON.
""".strip()

    return _wrap_llm_request(
        action="generate_questions",
        user_prompt=user_prompt,
        metadata={
            "topic_name": topic.name,
            "subject_name": topic.subject_name,
            "difficulty": difficulty,
            "count": count,
        },
    )


# =========================
# CHECK ANSWER
# =========================

def check_answer_request(
    question_object: Dict[str, Any],
    user_answer: Any,
) -> Dict[str, Any]:
    q = json.loads(json.dumps(question_object))
    q_json_str = json.dumps(q, ensure_ascii=False)
    user_answer_str = json.dumps(user_answer, ensure_ascii=False)

    user_prompt = f"""
You are in ANSWER CHECKING MODE.

Question JSON:
{q_json_str}

Student answer JSON:
{user_answer_str}

Compare the student's answer with the correct answer in the question.
Return ONLY a JSON object with this shape:

{{
  "kind": "answer_check",
  "question_id": string,
  "topic_name": string,
  "is_correct": boolean,
  "correct_answer": any,
  "explanation": string,
  "feedback": string,      // short, direct message to the student
  "score": number          // optional, 0.0 to 1.0
}}

Rules:
- Be strict but fair.
- If the answer is partially correct, set is_correct=false but explain what was right.
- Do NOT include any text outside this JSON.
""".strip()

    question_id = q.get("id", "")
    topic_name = q.get("topic_name", "")

    return _wrap_llm_request(
        action="check_answer",
        user_prompt=user_prompt,
        metadata={
            "question_id": question_id,
            "topic_name": topic_name,
        },
    )


# =========================
# PERFORMANCE TRACKING
# =========================

def update_performance(
    performance_store: Dict[str, Dict[str, Any]],
    topic_name: str,
    was_correct: bool,
    difficulty: Optional[str] = None,
) -> Dict[str, Any]:
    topic_name = (topic_name or "").strip()
    if not topic_name:
        return {"error": True, "reason": "missing_topic_name"}

    perf = _get_or_create_topic_perf(
        performance_store=performance_store,
        topic_name=topic_name,
    )

    perf.attempts += 1
    if was_correct:
        perf.correct += 1

    if difficulty:
        diff = difficulty.strip().lower()
        if diff in {"easy", "medium", "hard"}:
            perf.last_difficulty = diff

    perf.last_updated_iso = _now_iso()
    performance_store[topic_name] = _topic_perf_to_dict(perf)
    return _topic_perf_to_dict(perf)


def get_topic_stats(
    performance_store: Dict[str, Dict[str, Any]],
    topic_name: str,
) -> Dict[str, Any]:
    topic_name = (topic_name or "").strip()
    if not topic_name:
        return {"error": True, "reason": "missing_topic_name"}

    raw = performance_store.get(topic_name)
    if not raw:
        return {
            "topic_name": topic_name,
            "attempts": 0,
            "correct": 0,
            "accuracy": 0.0,
        }

    perf = _topic_perf_from_dict(raw)

    if perf.attempts == 0:
        accuracy = 0.0
    else:
        accuracy = perf.correct / perf.attempts

    return {
        "topic_name": perf.topic_name,
        "attempts": perf.attempts,
        "correct": perf.correct,
        "accuracy": accuracy,
    }


# =========================
# ROUTER
# =========================

def practice_llm_request(
    action: str,
    payload: Dict[str, Any],
    session_state: Dict[str, Any],
) -> Dict[str, Any]:
    raw_topics = session_state.get("topics") or []
    topics: List[Topic] = []
    for t in raw_topics:
        if isinstance(t, dict):
            topics.append(Topic(
                name=t.get("topic_name", ""),
                subject_name=t.get("subject_name", ""),
                weight=t.get("weight", "medium"),
                difficulty=t.get("difficulty", "medium"),
                weakness=t.get("weakness", "moderate"),
                progress=t.get("progress", 0.0),
                base_hours=t.get("base_hours", 2.0)
            ))
        else:
            topics.append(t)

    # Ensure practice_stats is always a dict stored back into session_state
    performance_store = session_state.get("practice_stats")
    if not isinstance(performance_store, dict):
        performance_store = {}
        session_state["practice_stats"] = performance_store  # persist it

    action = (action or "").strip().lower()

    if action == "generate_questions":
        topic_name = payload.get("topic_name", "")
        difficulty = payload.get("difficulty", "auto")
        count = int(payload.get("count", 5))

        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}

        return generate_practice_questions_request(
            topics=topics,
            performance_store=performance_store,
            topic_name=topic_name,
            difficulty=difficulty,
            count=count,
        )

    if action == "check_answer":
        question = payload.get("question")
        user_answer = payload.get("user_answer")

        if question is None:
            return {"error": True, "reason": "missing_question_object"}
        if user_answer is None:
            return {"error": True, "reason": "missing_user_answer"}

        return check_answer_request(
            question_object=question,
            user_answer=user_answer,
        )

    if action == "update_performance":
        topic_name = payload.get("topic_name", "")
        # was_correct must be a boolean; don't treat False as "missing"
        if "was_correct" not in payload:
            return {"error": True, "reason": "missing_was_correct"}
        was_correct = bool(payload["was_correct"])
        difficulty = payload.get("difficulty")

        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}

        updated = update_performance(
            performance_store=performance_store,
            topic_name=topic_name,
            was_correct=was_correct,
            difficulty=difficulty,
        )
        return {"ok": True, "updated": updated}

    if action == "topic_stats":
        topic_name = payload.get("topic_name", "")
        stats = get_topic_stats(
            performance_store=performance_store,
            topic_name=topic_name,
        )
        return {"kind": "topic_stats", "stats": stats}

    if action == "suggest_difficulty":
        topic_name = payload.get("topic_name", "")
        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}
        difficulty = suggest_difficulty_from_performance(
            performance_store=performance_store,
            topic_name=topic_name,
        )
        return {
            "kind": "suggested_difficulty",
            "topic_name": topic_name,
            "difficulty": difficulty,
        }

    if action == "start_practice":
        payload["count"] = payload.get("num_questions", 5)
        return practice_llm_request("generate_questions", payload, session_state)

    return {"error": True, "reason": f"unknown_practice_action: {action}"}
