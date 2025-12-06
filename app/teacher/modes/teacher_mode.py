from typing import Any, Dict, List, Optional
import json

from app.logic.scheduler import topic_to_dict, study_plan_to_dict, Topic, StudyPlan


base_system_prompt = """
You are an exam coach and subject-agnostic teacher.

Rules:
- Be direct and honest, not overly motivational or fake-positive.
- Explain things clearly for a college-level student.
- Focus on actionable study advice and exam strategy, not generic fluff.
- Always return VALID JSON ONLY. No extra text, no markdown, no explanations outside JSON.
""".strip()


def _find_topic(topics: List[Topic], topic_name: str) -> Optional[Topic]:
    target = topic_name.strip().lower()
    for t in topics:
        if t.name.strip().lower() == target:
            return t
    return None


def _wrap_llm_request(
    action: str,
    system_prompt: str,
    user_prompt: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    req: Dict[str, Any] = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "metadata": {"teacher_action": action},
    }
    if metadata:
        req["metadata"].update(metadata)
    return req


def topic_explain(
    topics: List[Topic],
    topic_name: str,
    level: str = "default",
) -> Dict[str, Any]:
    topic = _find_topic(topics, topic_name)
    if not topic:
        return {"error": True, "reason": f"topic_not_found: {topic_name}"}

    topic_data = topic_to_dict(topic)
    topic_json_str = json.dumps(topic_data, ensure_ascii=False)

    level = (level or "default").strip().lower()
    if level not in {"basic", "default", "deep"}:
        level = "default"

    user_prompt = f"""
You are in TEACHER MODE: explain a single topic in a structured way.

Student context (JSON):
{topic_json_str}

Level = "{level}":
- "basic": simpler explanation, more hand-holding, fewer details.
- "default": balanced level of detail and clarity.
- "deep": more nuance, exam strategy, and edge cases.

Return ONLY a JSON object with this exact shape (no extra keys):

{{
  "kind": "topic_explanation",
  "topic_name": string,
  "subject_name": string,
  "level": string,
  "summary": string,                // 2-4 sentences max
  "why_important": string,          // why this matters in exams / real usage
  "student_status": {{
    "difficulty": string,           // how hard this topic is
    "weight": string,               // exam importance
    "weakness": string,             // student's current weakness/strength
    "progress_comment": string      // comment based on their progress 0-1
  }},
  "main_ideas": [                   // 3-6 bullets
    {{
      "title": string,
      "description": string
    }}
  ],
  "recommended_study_plan": [       // ordered steps
    {{
      "step": integer,
      "title": string,
      "description": string
    }}
  ],
  "warnings": [string],             // time traps, common mistakes
  "tone": "direct"                  // always "direct"
}}

Output must be valid JSON. Do not include anything outside the JSON.
""".strip()

    return _wrap_llm_request(
        action="explain_topic",
        system_prompt=base_system_prompt,
        user_prompt=user_prompt,
        metadata={"topic_name": topic.name, "level": level},
    )


def summarize_topic_request(
    topics: List[Topic],
    topic_name: str,
) -> Dict[str, Any]:
    topic = _find_topic(topics, topic_name)
    if not topic:
        return {"error": True, "reason": f"topic_not_found: {topic_name}"}

    topic_data = topic_to_dict(topic)
    topic_json_str = json.dumps(topic_data, ensure_ascii=False)

    user_prompt = f"""
You are in SUMMARY MODE: create a compact summary of a topic for quick viewing.

Student topic JSON:
{topic_json_str}

Return ONLY a JSON object in this shape:

{{
  "kind": "topic_summary",
  "topic_name": string,
  "subject_name": string,
  "one_line_summary": string,      // max 1 sentence
  "progress_label": string,        // e.g. "0-25%", "25-50%", "50-75%", "75-100%"
  "risk_level": string,            // "low", "medium", "high" exam risk
  "exam_weight_label": string,     // short description of exam weight
  "recommended_focus": string,     // e.g. "focus on core concepts + medium questions"
  "tags": [string]                 // 3-6 tags (difficulty, weight, weakness, etc.)
}}

Do NOT include any text outside this JSON.
""".strip()

    return _wrap_llm_request(
        action="summarize_topic",
        system_prompt=base_system_prompt,
        user_prompt=user_prompt,
        metadata={"topic_name": topic.name},
    )


def give_examples_request(
    topics: List[Topic],
    topic_name: str,
    count: int = 2,
) -> Dict[str, Any]:
    topic = _find_topic(topics, topic_name)
    if not topic:
        return {"error": True, "reason": f"topic_not_found: {topic_name}"}

    topic_data = topic_to_dict(topic)
    topic_json_str = json.dumps(topic_data, ensure_ascii=False)
    count = max(1, count)

    user_prompt = f"""
You are in EXAMPLES MODE.

Goal:
- Suggest concrete study activities the student should DO for this topic.
- NOT content questions, but tasks like "write summary", "solve X questions", etc.

Topic JSON:
{topic_json_str}

The student requested around {count} examples.
Return ONLY a JSON object:

{{
  "kind": "topic_examples",
  "topic_name": string,
  "subject_name": string,
  "examples": [
    {{
      "title": string,
      "description": string,
      "estimated_time_minutes": integer,
      "type": string                 // e.g. "theory", "practice", "revision", "meta"
    }}
  ]
}}

Return between {count} and {count + 2} examples.
Use a direct, practical tone.
No output outside this JSON.
""".strip()

    return _wrap_llm_request(
        action="give_examples",
        system_prompt=base_system_prompt,
        user_prompt=user_prompt,
        metadata={"topic_name": topic.name, "requested_count": count},
    )


def build_check_understanding_request(
    topics: List[Topic],
    topic_name: str,
) -> Dict[str, Any]:
    topic = _find_topic(topics, topic_name)
    if topic is None:
        return {"error": True, "reason": f"topic_not_found: {topic_name}"}

    topic_data = topic_to_dict(topic)
    topic_json_str = json.dumps(topic_data, ensure_ascii=False)

    user_prompt = f"""
You are in UNDERSTANDING CHECK MODE.

Input topic JSON:
{topic_json_str}

You must generate a self-assessment checklist for the student.
Return ONLY a JSON object:

{{
  "kind": "topic_understanding_check",
  "topic_name": string,
  "subject_name": string,
  "overall_judgement": string,     // e.g. "weak", "partial", "strong", "overconfident"
  "questions": [                   // 4-8 self-check items
    {{
      "id": string,
      "prompt": string,            // yes/no or short-answer self-check
      "expected_if_strong": string // what a strong student should be able to do/say
    }}
  ],
  "red_flags": [string],           // patterns indicating poor understanding
  "advice_if_weak": string,
  "advice_if_okay": string,
  "advice_if_strong": string
}}

Keep it direct and exam-oriented.
No text outside this JSON.
""".strip()

    return _wrap_llm_request(
        action="check_topic_understanding",
        system_prompt=base_system_prompt,
        user_prompt=user_prompt,
        metadata={"topic_name": topic.name},
    )


def build_breakdown_steps_request(
    topics: List[Topic],
    topic_name: str,
) -> Dict[str, Any]:
    topic = _find_topic(topics, topic_name)
    if topic is None:
        return {"error": True, "reason": f"topic_not_found: {topic_name}"}

    topic_data = topic_to_dict(topic)
    topic_json_str = json.dumps(topic_data, ensure_ascii=False)

    user_prompt = f"""
You are in BREAKDOWN MODE.

Goal:
- Provide a step-by-step method for the student to study and understand this topic.
- Generic but practical, for a typical technical/theory topic.

Topic JSON:
{topic_json_str}

Return ONLY a JSON object:

{{
  "kind": "topic_breakdown_steps",
  "topic_name": string,
  "subject_name": string,
  "steps": [
    {{
      "step": integer,             // 1, 2, 3, ...
      "title": string,
      "description": string,
      "focus": string,             // "concepts", "practice", "revision", etc.
      "recommended_time_minutes": integer
    }}
  ],
  "emphasis": [string],            // 2-4 key points to focus on most
  "common_mistakes": [string]
}}

Steps must be ordered and realistic.
No fluff. No output outside JSON.
""".strip()

    return _wrap_llm_request(
        action="breakdown_steps",
        system_prompt=base_system_prompt,
        user_prompt=user_prompt,
        metadata={"topic_name": topic.name},
    )


def build_explain_study_plan_request(plan: StudyPlan) -> Dict[str, Any]:
    plan_data = study_plan_to_dict(plan)
    plan_json_str = json.dumps(plan_data, ensure_ascii=False)

    user_prompt = f"""
You are in PLAN EXPLANATION MODE.

The backend scheduler has generated this study plan JSON:
{plan_json_str}

Your job:
- Explain the plan to the student.
- Make clear what the overall strategy is.
- Summarise the next few days in a readable way.
- Be direct: if the plan is compressed/last-minute, say it clearly.

Return ONLY a JSON object:

{{
  "kind": "study_plan_explanation",
  "status": string,                    // reuse plan.status
  "status_comment": string,            // what that status means in normal words
  "overall_strategy": string,          // 2-4 sentences
  "key_principles": [string],          // 3-7 bullet points
  "day_summaries": [                   // summarise first 5-7 days
    {{
      "date": string,
      "total_hours": number,
      "main_focus": [string],          // topic or subject+topic labels
      "notes": string                  // short guidance for that day
    }}
  ]
}}

Do NOT include the full plan again; the backend already has it.
No output outside the JSON.
""".strip()

    return _wrap_llm_request(
        action="explain_study_plan",
        system_prompt=base_system_prompt,
        user_prompt=user_prompt,
        metadata={"plan_status": plan.status.value},
    )


def build_explain_today_request(
    plan: StudyPlan,
    today_iso: Optional[str] = None,
) -> Dict[str, Any]:
    plan_data = study_plan_to_dict(plan)
    plan_json_str = json.dumps(plan_data, ensure_ascii=False)

    user_prompt = f"""
You are in TODAY MODE.

You get:
- The full study plan JSON.
- The target date string for "today" (may or may not be inside plan).

Plan JSON:
{plan_json_str}

Today date (ISO string or null): {json.dumps(today_iso)}

Your job:
- Find the matching day for that date.
- If not found, fall back to the earliest day in the plan.
- If the plan has no days, say that.

Return ONLY a JSON object:

{{
  "kind": "today_explanation",
  "mode": string,                       // "exact_match", "fallback_first_day", "no_plan"
  "date": string | null,
  "total_hours": number | null,
  "tasks": [
    {{
      "topic_name": string,
      "subject_name": string,
      "task_type": string,
      "duration_hours": number,
      "how_to_approach": string
    }}
  ],
  "summary": string                     // short guidance for the day
}}

If plan has no days, set:
- mode = "no_plan"
- date = null
- total_hours = null
- tasks = []
No text outside the JSON.
""".strip()

    return _wrap_llm_request(
        action="explain_today",
        system_prompt=base_system_prompt,
        user_prompt=user_prompt,
        metadata={"today_iso": today_iso},
    )


def teacher_llm_request(
    action: str,
    payload: Dict[str, Any],
    session_state: Dict[str, Any],
) -> Dict[str, Any]:
    raw_topics = session_state.get("topics") or []
    topics: List[Topic] = []
    for t in raw_topics:
        if isinstance(t, dict):
            # Convert dict back to Topic object
            # Note: Ensure keys match Topic dataclass fields
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
    plan: Optional[StudyPlan] = session_state.get("plan")

    action = (action or "").strip().lower()

    if action == "explain_topic":
        topic_name = payload.get("topic_name", "")
        level = payload.get("level", "default")
        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}
        return topic_explain(topics=topics, topic_name=topic_name, level=level)

    if action == "summarize_topic":
        topic_name = payload.get("topic_name", "")
        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}
        return summarize_topic_request(topics=topics, topic_name=topic_name)

    if action == "give_examples":
        topic_name = payload.get("topic_name", "")
        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}
        count = int(payload.get("count", 2))
        return give_examples_request(topics=topics, topic_name=topic_name, count=count)

    if action == "check_understanding":
        topic_name = payload.get("topic_name", "")
        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}
        return build_check_understanding_request(topics=topics, topic_name=topic_name)

    if action == "breakdown_steps":
        topic_name = payload.get("topic_name", "")
        if not topic_name:
            return {"error": True, "reason": "missing_topic_name"}
        return build_breakdown_steps_request(topics=topics, topic_name=topic_name)

    if action == "explain_plan":
        if plan is None:
            return {"error": True, "reason": "plan_not_in_session_state"}
        return build_explain_study_plan_request(plan=plan)

    if action == "explain_today":
        if plan is None:
            return {"error": True, "reason": "plan_not_in_session_state"}
        today = payload.get("today_iso")
        return build_explain_today_request(plan=plan, today_iso=today)

    return {"error": True, "reason": f"unknown_teacher_action {action}"}
