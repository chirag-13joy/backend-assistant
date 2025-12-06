from typing import Any, Dict, List, Optional
import json

from app.logic.scheduler import (
    Topic,
    compute_priority_score,
    estimate_required_hours,
    topic_to_dict,
)

# =========================
# BASE SYSTEM PROMPT
# =========================

revision_system_prompt = """
You are an exam-focused revision helper.

Rules:
- Be concise and brutally focused on what matters for exams.
- Prefer bullet points and short statements over long explanations.
- Assume the student is revising, not learning from scratch.
- Always return VALID JSON ONLY. No text, no markdown, no commentary outside JSON.
""".strip()


def _wrap_llm_request(
    action: str,
    user_prompt: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Standard wrapper for LLM API calls (same pattern as teacher/practice).
    Dev2 will call the actual LLM with this dict.
    """
    req: Dict[str, Any] = {
        "messages": [
            {"role": "system", "content": revision_system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "metadata": {"revision_action": action},
    }

    if metadata:
        req["metadata"].update(metadata)

    return req


def _find_topic(topics: List[Topic], topic_name: str) -> Optional[Topic]:
    """
    Case-insensitive lookup of a Topic by name.
    """
    target = (topic_name or "").strip().lower()
    for topic in topics:
        if topic.name.strip().lower() == target:
            return topic
    return None


# =========================
# 1) REVISION POINTS
# =========================

def build_revision_points_request(
    topics: List[Topic],
    topic_name: str,
) -> Dict[str, Any]:
    topic = _find_topic(topics, topic_name)
    if topic is None:
        return {"error": True, "reason": f"topic_not_found: {topic_name}"}

    topic_data = topic_to_dict(topic)
    topic_json_str = json.dumps(topic_data, ensure_ascii=False)

    user_prompt = f"""
You are in REVISION POINTS MODE.

Student topic JSON:
{topic_json_str}

Goal:
- Create a SHORT, HIGH-YIELD revision summary for quick review.
- Focus only on core ideas and exam-relevant facts, not teaching from scratch.

Return ONLY a JSON object with this shape:

{{
  "kind": "revision_points",
  "topic_name": string,
  "subject_name": string,
  "bullets": [string],               // 3-7 short bullet points
  "key_definitions": [string],       // 1-3 very important definitions
  "key_formulas_or_rules": [string], // 0-5 formulas or rules (if applicable)
  "quick_example": string,           // one simple example or scenario
  "common_mistakes": [string]        // optional; 0-5 typical errors (can be empty)
}}

Constraints:
- Keep bullets short, like flash notes.
- Use direct, exam-focused language.
- Do NOT include any text outside the JSON.
""".strip()

    return _wrap_llm_request(
        action="revision_points",
        user_prompt=user_prompt,
        metadata={
            "topic_name": topic.name,
            "subject_name": topic.subject_name,
        },
    )


# =========================
# 2) REVISION FLASHCARDS
# =========================

def build_revision_flashcards_request(
    topics: List[Topic],
    topic_name: str,
    count: int,
) -> Dict[str, Any]:
    topic = _find_topic(topics, topic_name)
    if topic is None:
        return {"error": True, "reason": f"topic_not_found: {topic_name}"}

    topic_data = topic_to_dict(topic)
    topic_json_str = json.dumps(topic_data, ensure_ascii=False)

    count = max(1, int(count))

    user_prompt = f"""
You are in REVISION FLASHCARD MODE.

Student topic JSON:
{topic_json_str}

Goal:
- Create flashcards for fast recall.
- Each flashcard has a 'front' (prompt/question) and 'back' (answer).

You must generate EXACTLY {count} flashcards.

Return ONLY a JSON object with this shape:

{{
  "kind": "revision_flashcards",
  "topic_name": string,
  "subject_name": string,
  "count": number,
  "flashcards": [
    {{
      "id": string,
      "front": string,   // question / cue
      "back": string     // answer / key idea
    }}
  ]
}}

Rules:
- Flashcards should target definitions, core concepts, formulas, typical exam traps.
- Use clear, concise wording.
- Do NOT include any text outside the JSON.
""".strip()

    return _wrap_llm_request(
        action="revision_flashcards",
        user_prompt=user_prompt,
        metadata={
            "topic_name": topic.name,
            "subject_name": topic.subject_name,
            "requested_count": count,
        },
    )


# =========================
# 3) HIGH-YIELD TOPICS (pure Python)
# =========================

def select_high_yield_topics(
    topics: List[Topic],
    fraction: float = 0.3,
    min_count: int = 3,
) -> Dict[str, Any]:
    """
    Pure Python, no LLM:
    - Uses compute_priority_score (weight + weakness + difficulty)
    - Uses estimate_required_hours (remaining work)
    to rank topics and return the top ~fraction (20–30%) as high-yield.
    """
    if not topics:
        return {
            "kind": "high_yield_topics",
            "total_topics": 0,
            "selected_count": 0,
            "topics": [],
        }

    scored: List[Dict[str, Any]] = []
    for t in topics:
        priority = float(compute_priority_score(t))
        remaining_hours = float(estimate_required_hours(t))
        combined_score = priority * (1.0 + remaining_hours)

        scored.append(
            {
                "topic": topic_to_dict(t),
                "priority_score": priority,
                "estimated_remaining_hours": remaining_hours,
                "combined_score": combined_score,
            }
        )

    # Sort by combined_score descending
    scored.sort(key=lambda x: x["combined_score"], reverse=True)

    n = len(scored)
    top_n = max(min_count, int(n * fraction))
    top_n = min(top_n, n)

    selected = scored[:top_n]

    # Add rank for UI display
    for idx, item in enumerate(selected, start=1):
        item["rank"] = idx

    return {
        "kind": "high_yield_topics",
        "total_topics": n,
        "selected_count": top_n,
        "topics": selected,
    }


# =========================
# 4) LAST-MINUTE REVISION
# =========================

def build_last_minute_revision_request(
    topics: List[Topic],
    topic_name: str,
) -> Dict[str, Any]:
    topic = _find_topic(topics, topic_name)
    if topic is None:
        return {"error": True, "reason": f"topic_not_found: {topic_name}"}

    topic_data = topic_to_dict(topic)
    topic_json_str = json.dumps(topic_data, ensure_ascii=False)

    user_prompt = f"""
You are in LAST-MINUTE REVISION MODE.

Student topic JSON:
{topic_json_str}

The student is revising just before the exam.
Goal:
- Provide an ultra-compressed set of reminder bullets.
- Only the absolute MUST-REMEMBER facts.

Return ONLY a JSON object with this shape:

{{
  "kind": "last_minute_revision",
  "topic_name": string,
  "subject_name": string,
  "bullets": [string]  // EXACTLY 3 bullets, no explanations
}}

Rules:
- EXACTLY 3 bullets.
- Each bullet should be one short sentence or phrase.
- No intros, no explanations, no extra commentary.
- Do NOT include any text outside the JSON.
""".strip()

    return _wrap_llm_request(
        action="last_minute_revision",
        user_prompt=user_prompt,
        metadata={
            "topic_name": topic.name,
            "subject_name": topic.subject_name,
        },
    )


# =========================
# 5) EXPECTED EXAM QUESTIONS
# =========================

def build_expected_exam_questions_request(
    topics: List[Topic],
    topic_name: str,
    count: int,
) -> Dict[str, Any]:
    topic = _find_topic(topics, topic_name)
    if topic is None:
        return {"error": True, "reason": f"topic_not_found: {topic_name}"}

    topic_data = topic_to_dict(topic)
    topic_json_str = json.dumps(topic_data, ensure_ascii=False)

    count = max(1, int(count))

    user_prompt = f"""
You are in EXPECTED EXAM QUESTIONS MODE.

Student topic JSON:
{topic_json_str}

Goal:
- Suggest likely exam questions for this topic based on typical patterns.
- Mix of short-answer, 2-mark, 5-mark, and application-based questions.

You must generate BETWEEN {count} and {count + 2} questions.

Return ONLY a JSON object with this shape:

{{
  "kind": "expected_exam_questions",
  "topic_name": string,
  "subject_name": string,
  "questions": [
    {{
      "id": string,
      "question_type": string,   // "short", "2-mark", "5-mark", "application"
      "marks": number,           // suggested marks (e.g. 2, 5, 10)
      "prompt": string,
      "hint": string,            // optional hint/outline (can be empty string)
      "difficulty": string       // "easy" | "medium" | "hard"
    }}
  ]
}}

Rules:
- Questions must be realistic for a college/university exam.
- Avoid extremely niche or trivial questions.
- Prefer coverage of different sub-concepts of the topic.
- Do NOT include any text outside the JSON.
""".strip()

    return _wrap_llm_request(
        action="expected_exam_questions",
        user_prompt=user_prompt,
        metadata={
            "topic_name": topic.name,
            "subject_name": topic.subject_name,
            "requested_count": count,
        },
    )


# =========================
# ROUTER
# =========================

def revision_llm_request(
    action: str,
    payload: Dict[str, Any],
    session_state: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Main entrypoint for Revision Mode.

    action:
      - "revision_points"
      - "revision_flashcards"
      - "high_yield_topics"
      - "last_minute_revision"
      - "expected_exam_questions"

    session_state:
      - should contain "topics": List[Topic]
    """
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
    action = (action or "").strip().lower()

    if action == "revision_points":
        topic_name = payload.get("topic_name", "")
        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}
        return build_revision_points_request(
            topics=topics,
            topic_name=topic_name,
        )

    if action == "revision_flashcards":
        topic_name = payload.get("topic_name", "")
        count = int(payload.get("count", 5))
        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}
        return build_revision_flashcards_request(
            topics=topics,
            topic_name=topic_name,
            count=count,
        )

    if action == "high_yield_topics":
        fraction = float(payload.get("fraction", 0.3))
        min_count = int(payload.get("min_count", 3))
        return select_high_yield_topics(
            topics=topics,
            fraction=fraction,
            min_count=min_count,
        )

    if action == "last_minute_revision":
        topic_name = payload.get("topic_name", "")
        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}
        return build_last_minute_revision_request(
            topics=topics,
            topic_name=topic_name,
        )

    if action == "expected_exam_questions":
        topic_name = payload.get("topic_name", "")
        count = int(payload.get("count", 5))
        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}
        return build_expected_exam_questions_request(
            topics=topics,
            topic_name=topic_name,
            count=count,
        )

    if action == "generate_revision_plan":
        # This maps to high_yield_topics but formatted for the frontend
        fraction = float(payload.get("fraction", 0.5))
        min_count = int(payload.get("min_count", 3))
        
        high_yield_result = select_high_yield_topics(
            topics=topics,
            fraction=fraction,
            min_count=min_count,
        )
        
        # Transform for frontend
        revision_topics = []
        for item in high_yield_result.get("topics", []):
            t_dict = item.get("topic", {})
            revision_topics.append({
                "subject": t_dict.get("subject_name", "Unknown"),
                "topic": t_dict.get("topic_name", "Unknown"),
                "weakness": t_dict.get("weakness", "moderate"),
                "priority": f"Score: {item.get('priority_score', 0):.2f}"
            })
            
        return {
            "kind": "revision_plan",
            "revision_topics": revision_topics
        }

    return {"error": True, "reason": f"unknown_revision_action: {action}"}
