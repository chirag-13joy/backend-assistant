from enum import Enum
from dataclasses import dataclass, field,asdict 
from typing import List, Dict, Any
from datetime import date, timedelta
import re



# ENUMS
class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Weight(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Weakness(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


class TaskType(str, Enum):
    THEORY = "theory"
    PRACTICE = "practice"
    REVISION = "revision"


class PlanStatus(str, Enum):
    REALISTIC = "realistic"
    COMPRESSED = "compressed"
    HIGH_YIELD_ONLY = "high_yield_only"
    LAST_MINUTE = "last_minute"


# DATA MODELS
@dataclass
class Topic:
    name: str
    subject_name: str
    weight: Weight
    difficulty: Difficulty
    weakness: Weakness
    progress: float
    base_hours: float


@dataclass
class Task:
    topic_name: str
    subject_name: str
    task_type: TaskType
    duration_hours: float
    priority_score: float


@dataclass
class PlanDay:
    date: date
    tasks: List[Task] = field(default_factory=list)
    total_hours: float = 0.0


@dataclass
class StudyPlan:
    days: List[PlanDay]
    start_date: date
    exam_date: date
    hours_per_day: float
    status: PlanStatus


# NORMALIZERS
def _clean_text(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = text.strip(" .,!?:;-/\\")
    return text


# DIFFICULTY
_DIFFICULTY_MAP: Dict[str, Difficulty] = {
    # EASY
    "easy": Difficulty.EASY,
    "e": Difficulty.EASY,
    "ez": Difficulty.EASY,
    "simple": Difficulty.EASY,
    "basic": Difficulty.EASY,
    "beginner": Difficulty.EASY,
    "begginer": Difficulty.EASY,
    "intro": Difficulty.EASY,
    "introductory": Difficulty.EASY,
    "trivial": Difficulty.EASY,
    "no brainer": Difficulty.EASY,
    "no-brainer": Difficulty.EASY,
    "light": Difficulty.EASY,
    "chill": Difficulty.EASY,
    "easy peasy": Difficulty.EASY,
    "easy-peasy": Difficulty.EASY,

    # MEDIUM
    "medium": Difficulty.MEDIUM,
    "moderate": Difficulty.MEDIUM,
    "modrate": Difficulty.MEDIUM,
    "average": Difficulty.MEDIUM,
    "mid": Difficulty.MEDIUM,
    "normal": Difficulty.MEDIUM,
    "ok": Difficulty.MEDIUM,
    "okay": Difficulty.MEDIUM,
    "decent": Difficulty.MEDIUM,
    "manageable": Difficulty.MEDIUM,
    "intermediate": Difficulty.MEDIUM,

    # HARD
    "hard": Difficulty.HARD,
    "difficult": Difficulty.HARD,
    "diffficult": Difficulty.HARD,
    "dificult": Difficulty.HARD,
    "tough": Difficulty.HARD,
    "tuf": Difficulty.HARD,
    "tuff": Difficulty.HARD,
    "complex": Difficulty.HARD,
    "challenging": Difficulty.HARD,
    "chalenging": Difficulty.HARD,
    "challange": Difficulty.HARD,
    "advanced": Difficulty.HARD,
    "intense": Difficulty.HARD,
    "brutal": Difficulty.HARD,
    "nightmare": Difficulty.HARD,
}


def normalize_difficulty(value: str) -> Difficulty:
    if not value:
        return Difficulty.MEDIUM

    text = _clean_text(value)

    if text in _DIFFICULTY_MAP:
        return _DIFFICULTY_MAP[text]

    for key, enum_value in _DIFFICULTY_MAP.items():
        if key in text:
            return enum_value

    if any(w in text for w in ["hard", "diff", "tough", "complex", "advanc"]):
        return Difficulty.HARD
    if any(w in text for w in ["easy", "simple", "basic", "intro"]):
        return Difficulty.EASY

    return Difficulty.MEDIUM


# WEIGHT
_WEIGHT_MAP: Dict[str, Weight] = {
    # HIGH
    "high": Weight.HIGH,
    "important": Weight.HIGH,
    "major": Weight.HIGH,
    "critical": Weight.HIGH,
    "crtical": Weight.HIGH,
    "vital": Weight.HIGH,
    "key": Weight.HIGH,
    "core": Weight.HIGH,
    "essential": Weight.HIGH,
    "must do": Weight.HIGH,
    "must-do": Weight.HIGH,
    "urgent": Weight.HIGH,
    "top": Weight.HIGH,
    "top priority": Weight.HIGH,
    "high priority": Weight.HIGH,
    "exam heavy": Weight.HIGH,
    "exam-heavy": Weight.HIGH,

    # MEDIUM
    "medium": Weight.MEDIUM,
    "mid": Weight.MEDIUM,
    "moderate": Weight.MEDIUM,
    "modrate": Weight.MEDIUM,
    "average": Weight.MEDIUM,
    "normal": Weight.MEDIUM,
    "balanced": Weight.MEDIUM,
    "standard": Weight.MEDIUM,
    "okay": Weight.MEDIUM,
    "ok": Weight.MEDIUM,
    "decent": Weight.MEDIUM,
    "medium priority": Weight.MEDIUM,

    # LOW
    "low": Weight.LOW,
    "minor": Weight.LOW,
    "less important": Weight.LOW,
    "unimportant": Weight.LOW,
    "not important": Weight.LOW,
    "trivial": Weight.LOW,
    "extra": Weight.LOW,
    "bonus": Weight.LOW,
    "filler": Weight.LOW,
    "side topic": Weight.LOW,
    "side-topic": Weight.LOW,
    "optional": Weight.LOW,
    "can skip": Weight.LOW,
    "can-skip": Weight.LOW,
}


def normalize_weight(value: str) -> Weight:
    if not value:
        return Weight.MEDIUM

    text = _clean_text(value)

    if text in _WEIGHT_MAP:
        return _WEIGHT_MAP[text]

    for key, enum_value in _WEIGHT_MAP.items():
        if key in text:
            return enum_value

    if any(w in text for w in ["high", "important", "vital", "core", "urgent"]):
        return Weight.HIGH
    if any(w in text for w in ["low", "minor", "optional", "extra", "filler"]):
        return Weight.LOW

    return Weight.MEDIUM


# WEAKNESS
_WEAKNESS_MAP: Dict[str, Weakness] = {
    # WEAK
    "weak": Weakness.WEAK,
    "bad": Weakness.WEAK,
    "poor": Weakness.WEAK,
    "confused": Weakness.WEAK,
    "cnofused": Weakness.WEAK,
    "lost": Weakness.WEAK,
    "no idea": Weakness.WEAK,
    "no clue": Weakness.WEAK,
    "clueless": Weakness.WEAK,
    "struggle": Weakness.WEAK,
    "strugle": Weakness.WEAK,
    "struggling": Weakness.WEAK,
    "not confident": Weakness.WEAK,
    "low confidence": Weakness.WEAK,
    "hate this": Weakness.WEAK,
    "scary topic": Weakness.WEAK,
    "panic": Weakness.WEAK,
    "panic mode": Weakness.WEAK,

    # MODERATE
    "moderate": Weakness.MODERATE,
    "modrate": Weakness.MODERATE,
    "average": Weakness.MODERATE,
    "avg": Weakness.MODERATE,
    "okay": Weakness.MODERATE,
    "ok": Weakness.MODERATE,
    "decent": Weakness.MODERATE,
    "mid": Weakness.MODERATE,
    "manageable": Weakness.MODERATE,
    "50 50": Weakness.MODERATE,
    "50-50": Weakness.MODERATE,
    "mixed": Weakness.MODERATE,
    "getting there": Weakness.MODERATE,

    # STRONG
    "strong": Weakness.STRONG,
    "good": Weakness.STRONG,
    "confident": Weakness.STRONG,
    "very confident": Weakness.STRONG,
    "solid": Weakness.STRONG,
    "clear": Weakness.STRONG,
    "comfortable": Weakness.STRONG,
    "mastered": Weakness.STRONG,
    "fluent": Weakness.STRONG,
    "easy for me": Weakness.STRONG,
}


def normalize_weakness(value: str) -> Weakness:
    if not value:
        return Weakness.MODERATE

    text = _clean_text(value)

    if text in _WEAKNESS_MAP:
        return _WEAKNESS_MAP[text]

    for key, enum_value in _WEAKNESS_MAP.items():
        if key in text:
            return enum_value

    if any(w in text for w in ["no idea", "clueless", "strug", "panic", "lost"]):
        return Weakness.WEAK
    if any(w in text for w in ["strong", "confident", "master", "comfortable"]):
        return Weakness.STRONG

    return Weakness.MODERATE

#Building topics from raw payload
def build_topics_from_payload(payload: list[dict[str, Any]]) ->list[Topic]:
    topics: list[Topic]=[]
    for item in payload:
        subject_name= item["subject_name"]
        topic_name=item["topic_name"]
        difficulty=normalize_difficulty(item.get("difficulty","medium"))
        weight=normalize_weight(item.get("weight","medium"))
        weakness=normalize_weakness(item.get("weakness","moderate"))
        progress=float(item.get("progress",0))
        if progress>1.0:
            progress/=100.0
        base_hours=float(item.get("base_hours",2.0))
        topics.append(
            Topic(
                name=topic_name,
                subject_name=subject_name,
                weight=weight,
                difficulty=difficulty,
                weakness=weakness,
                progress=progress,
                base_hours=base_hours
                )
            )
    return topics

#scoring helpers
def _weight_value(weight: Weight)-> float:
    if weight==Weight.HIGH:
        return 1
    elif weight==Weight.MEDIUM:
        return 0.6
    else:
        return 0.3
    
def _weakness_value(weakness: Weakness)-> float:
    if weakness==Weakness.WEAK:
        return 1
    elif weakness==Weakness.MODERATE:
        return 0.6
    else:
        return 0.3
    
def _difficulty_value(difficulty: Difficulty) -> float:
    if difficulty == Difficulty.HARD:
        return 1
    elif difficulty == Difficulty.MEDIUM:
        return 0.7
    else:
        return 0.4

    
def compute_priority_score(topic: Topic)->float:
    weight=_weight_value(topic.weight)
    weakness=_weakness_value(topic.weakness)
    difficulty=_difficulty_value(topic.difficulty)
    priority_score=(weight*0.5)+(weakness*0.3)+(difficulty*0.2)
    return priority_score

def estimate_required_hours(topic: Topic) -> float:
    remaining_progress = max(0.0, 1 - topic.progress)

    if topic.difficulty == Difficulty.EASY:
        diff_factor = 0.8
    elif topic.difficulty == Difficulty.HARD:
        diff_factor = 1.2
    else:
        diff_factor = 1.0

    required_hours = topic.base_hours * remaining_progress * diff_factor
    return required_hours


def generate_tasks_for_a_topic(topic: Topic) -> List[Task]:
    tasks: List[Task] = []

    total_hours = estimate_required_hours(topic)
    if total_hours <= 0:
        return tasks

    priority_score = compute_priority_score(topic)

    theory_hours = total_hours * 0.4
    practice_hours = total_hours * 0.4
    revision_hours = total_hours * 0.2


    if theory_hours > 0.1:
        tasks.append(
            Task(
                topic_name=topic.name,
                subject_name=topic.subject_name,
                task_type=TaskType.THEORY,
                duration_hours=theory_hours,
                priority_score=priority_score,
            )
        )

    if practice_hours > 0.1:
        tasks.append(
            Task(
                topic_name=topic.name,
                subject_name=topic.subject_name,
                task_type=TaskType.PRACTICE,
                duration_hours=practice_hours,
                priority_score=priority_score,
            )
        )
    
    if revision_hours>0.1:
        tasks.append(
            Task(
                topic_name=topic.name,
                subject_name=topic.subject_name,
                task_type=TaskType.REVISION,
                duration_hours=revision_hours,
                priority_score=priority_score,
            )
        )
    return tasks

def build_task_list(topics: List[Topic]) -> List[Task]:
    all_tasks: List[Task] = []
    for topic in topics:
        all_tasks.extend(generate_tasks_for_a_topic(topic))

    all_tasks.sort(key=lambda x: x.priority_score, reverse=True)
    return all_tasks


#Trims less priority tasks when time is limited
def trim_low_priority_tasks(tasks: List[Task],total_available_hours: float) -> List[Task]:
    trimmed=[]
    used=0.0
    for task in tasks:
        if task.duration_hours<=0:
            continue
        if used+task.duration_hours<=total_available_hours:
            trimmed.append(task)
            used+=task.duration_hours
        else:
            continue
    return trimmed
    
def schedule_from_tasks(
    tasks: List[Task],
    start_date: date,
    exam_date: date,
    hours_per_day: float,
    initial_status: PlanStatus
) -> StudyPlan:
    # Work on a local copy so we don't mutate the caller's list
    tasks = [
        Task(
            topic_name=t.topic_name,
            subject_name=t.subject_name,
            task_type=t.task_type,
            duration_hours=t.duration_hours,
            priority_score=t.priority_score,
        )
        for t in tasks
    ]

    days: List[PlanDay] = []
    current_date = start_date
    days_left = (exam_date - start_date).days

    if days_left <= 0:
        days_left = 1  # last day

    task_index = 0
    status = initial_status

    for _ in range(days_left):
        remaining_hours = hours_per_day
        day_tasks: List[Task] = []

        while remaining_hours > 0 and task_index < len(tasks):
            current_task = tasks[task_index]

            # 🔹 Skip tasks that are effectively zero duration
            if current_task.duration_hours <= 1e-6:
                task_index += 1
                continue

            if current_task.duration_hours <= remaining_hours:
                day_tasks.append(current_task)
                remaining_hours -= current_task.duration_hours
                task_index += 1
            else:
                part_task = Task(
                    topic_name=current_task.topic_name,
                    subject_name=current_task.subject_name,
                    task_type=current_task.task_type,
                    duration_hours=remaining_hours,
                    priority_score=current_task.priority_score,
                )
                day_tasks.append(part_task)
                current_task.duration_hours -= remaining_hours
                remaining_hours = 0

        used_hours = hours_per_day - remaining_hours
        days.append(
            PlanDay(
                date=current_date,
                tasks=day_tasks,
                total_hours=used_hours,
            )
        )
        current_date += timedelta(days=1)

        if task_index >= len(tasks):
            break

    # if we still have tasks left and status wasn't compressed, mark as high_yield_only
    if task_index < len(tasks) and status == PlanStatus.REALISTIC:
        status = PlanStatus.HIGH_YIELD_ONLY

    return StudyPlan(
        days=days,
        start_date=start_date,
        exam_date=exam_date,
        hours_per_day=hours_per_day,
        status=status,
    )


def generate_last_minute_plan(topics: List[Topic],
                              start_date:date,
                              exam_date:date,
                              hours_per_day:float)->StudyPlan:
    tasks=build_task_list(topics)
    if not tasks:
        return StudyPlan(
            days=[],
            start_date=start_date,
            exam_date=exam_date,
            hours_per_day=hours_per_day,
            status=PlanStatus.LAST_MINUTE,
        )

    
    tasks.sort(key=lambda x:x.priority_score, reverse=True)
    top_count=max(1,int(len(tasks)*0.3))
    tasks=tasks[:top_count]
    days_left=max(1,(exam_date-start_date).days)
    total_available_hours=days_left*hours_per_day
    tasks=trim_low_priority_tasks(tasks,total_available_hours)
    return schedule_from_tasks(
        tasks=tasks,
        start_date=start_date,
        exam_date=exam_date,
        hours_per_day=hours_per_day,
        initial_status=PlanStatus.LAST_MINUTE
    )

def generate_study_plan(topics:List[Topic],
                        start_date:date,
                        exam_date:date,
                        hours_per_day:float,
                        )->StudyPlan:
    days_left=(exam_date-start_date).days
    if days_left<=0:
        return generate_last_minute_plan(topics=topics,
                                   start_date=start_date,
                                   exam_date=exam_date,
                                   hours_per_day=hours_per_day)
    tasks=build_task_list(topics)
    total_required_hours=sum(t.duration_hours for t in tasks)
    total_available_hours=days_left*hours_per_day

    if total_required_hours <= total_available_hours:
        status = PlanStatus.REALISTIC
    else:
        status = PlanStatus.COMPRESSED
        tasks = trim_low_priority_tasks(tasks, total_available_hours)

    return schedule_from_tasks(
        tasks=tasks,
        start_date=start_date,
        exam_date=exam_date,
        hours_per_day=hours_per_day,
        initial_status=status
    )

# ============ SERIALIZATION HELPERS (for API / LLM / frontend) ============

def _serialize_value(value: Any):
    from enum import Enum as _Enum
    from datetime import date as _Date

    # Enums -> their string value
    if isinstance(value, _Enum):
        return value.value

    # date -> ISO string
    if isinstance(value, _Date):
        return value.isoformat()

    # dataclasses -> dict
    if hasattr(value, "__dataclass_fields__"):
        return {k: _serialize_value(v) for k, v in asdict(value).items()}

    # list -> list
    if isinstance(value, list):
        return [_serialize_value(v) for v in value]

    # dict -> dict
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}

    # primitives
    return value

def topic_to_dict(topic: Topic) -> Dict[str,Any]:
    return _serialize_value(topic)

def study_plan_to_dict(plan: StudyPlan) -> Dict[str, Any]:
    """
    Convert StudyPlan -> plain dict with only JSON-safe values:
    - enums as strings
    - dates as ISO strings
    """
    return _serialize_value(plan)
