import datetime
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import (
    StudyGroup,
    GroupMember,
    TeachingPair,
    StudySchedule,
    Student,
    SkillProfile,
    Topic,
)
from auth import get_current_user, require_teacher, require_student
from ml.group_matcher import (
    form_balanced_study_groups,
    generate_peer_teaching_recommendations,
    match_study_schedules,
)

router = APIRouter()


# ─────────────────────────────────────────────
# PYDANTIC SCHEMAS
# ─────────────────────────────────────────────

class ScheduleSlotCreate(BaseModel):
    day_of_week: str = Field(..., example="Monday")
    start_time: str = Field(..., example="17:00")
    end_time: str = Field(..., example="19:00")


class ScheduleSlotOut(BaseModel):
    id: int
    day_of_week: str
    start_time: str
    end_time: str
    is_available: bool

    class Config:
        from_attributes = True


class PeerTeachingItem(BaseModel):
    id: Optional[int] = None
    tutor_id: int
    tutor_name: str
    learner_id: int
    learner_name: str
    topic_name: str
    reason: str
    status: Optional[str] = "recommended"


class GroupMemberSummary(BaseModel):
    student_id: int
    name: str
    role: str
    strong_topics: List[str]
    weak_topics: List[str]


class StudyGroupDetailOut(BaseModel):
    id: int
    name: str
    status: str
    member_count: int
    coverage_rate: float
    covered_topics: List[str]
    uncovered_topics: List[str]
    members: List[GroupMemberSummary]
    teaching_pairs: List[PeerTeachingItem]
    common_schedules: List[Dict[str, Any]] = []
    created_at: datetime.datetime


class GenerateGroupsRequest(BaseModel):
    min_size: Optional[int] = 3
    max_size: Optional[int] = 5
    reset_existing: Optional[bool] = True


# ─────────────────────────────────────────────
# STUDY SCHEDULE MANAGEMENT
# ─────────────────────────────────────────────

@router.get("/schedules/my", response_model=List[ScheduleSlotOut])
def get_my_study_schedules(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current student's weekly study availability slots.
    """
    slots = (
        db.query(StudySchedule)
        .filter(StudySchedule.student_id == current_user.id, StudySchedule.is_available == True)
        .order_by(StudySchedule.day_of_week, StudySchedule.start_time)
        .all()
    )
    return slots


@router.post("/schedules", response_model=ScheduleSlotOut, status_code=status.HTTP_201_CREATED)
def add_study_schedule_slot(
    req: ScheduleSlotCreate,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a weekly available study time slot.
    """
    existing = db.query(StudySchedule).filter(
        StudySchedule.student_id == current_user.id,
        StudySchedule.day_of_week == req.day_of_week,
        StudySchedule.start_time == req.start_time,
    ).first()
    if existing:
        existing.end_time = req.end_time
        existing.is_available = True
        db.commit()
        db.refresh(existing)
        return existing

    slot = StudySchedule(
        student_id=current_user.id,
        day_of_week=req.day_of_week,
        start_time=req.start_time,
        end_time=req.end_time,
        is_available=True,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.delete("/schedules/{schedule_id}")
def delete_study_schedule_slot(
    schedule_id: int,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove an availability slot.
    """
    slot = db.query(StudySchedule).filter(
        StudySchedule.id == schedule_id,
        StudySchedule.student_id == current_user.id
    ).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Schedule slot not found.")
    db.delete(slot)
    db.commit()
    return {"message": "Schedule slot deleted successfully."}


# ─────────────────────────────────────────────
# INTELLIGENT STUDY GROUP FORMATION (TEACHER)
# ─────────────────────────────────────────────

@router.post("/groups/generate", response_model=List[StudyGroupDetailOut])
def generate_study_groups(
    req: GenerateGroupsRequest = GenerateGroupsRequest(),
    current_user: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Teacher Only: Execute the Optimization Grouping Matcher.
    Partitions students into balanced groups of 3 to 5 where weak topics are
    covered by strong members, persists to PostgreSQL, and computes peer teaching pairs.
    """
    # 1. Fetch all students with role='student'
    students = db.query(Student).filter(Student.role == "student").all()
    if len(students) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 active students are required to form study groups.",
        )

    # 2. Build student skill profiles representation
    student_payloads = []
    for s in students:
        skills = db.query(SkillProfile).filter(SkillProfile.student_id == s.id).all()
        weak_topics = [sp.topic for sp in skills if sp.status == "weak"]
        strong_topics = [sp.topic for sp in skills if sp.status == "strong"]
        mastery = {sp.topic: sp.mastery_score for sp in skills}

        student_payloads.append({
            "id": s.id,
            "name": s.name,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "mastery_scores": mastery,
        })

    # 3. Run Optimization Group Matching Algorithm
    formed_groups = form_balanced_study_groups(
        students=student_payloads,
        min_size=req.min_size or 3,
        max_size=req.max_size or 5,
    )

    if req.reset_existing:
        # Clear existing auto-generated active groups
        old_groups = db.query(StudyGroup).filter(StudyGroup.status == "active").all()
        for og in old_groups:
            db.delete(og)
        db.commit()

    # 4. Persist to PostgreSQL
    results: List[StudyGroupDetailOut] = []

    for g_data in formed_groups:
        group_obj = StudyGroup(
            name=g_data["group_name"],
            status="active",
            created_at=datetime.datetime.utcnow(),
        )
        db.add(group_obj)
        db.commit()
        db.refresh(group_obj)

        # Add Members
        members_summary: List[GroupMemberSummary] = []
        member_ids = [m["id"] for m in g_data["members"]]
        member_names = {m["id"]: m["name"] for m in g_data["members"]}

        for idx, m_dict in enumerate(g_data["members"]):
            role = "lead" if idx == 0 else "member"
            gm = GroupMember(
                group_id=group_obj.id,
                student_id=m_dict["id"],
                role=role,
                joined_at=datetime.datetime.utcnow(),
            )
            db.add(gm)
            members_summary.append(GroupMemberSummary(
                student_id=m_dict["id"],
                name=m_dict["name"],
                role=role,
                strong_topics=m_dict["strong_topics"],
                weak_topics=m_dict["weak_topics"],
            ))
        db.commit()

        # Generate & Persist Peer-Teaching Pairs
        teaching_pairs_raw = generate_peer_teaching_recommendations(g_data["members"])
        teaching_pairs_out: List[PeerTeachingItem] = []

        for p in teaching_pairs_raw:
            # Find topic_id if exists
            topic_record = db.query(Topic).filter(Topic.name == p["topic_name"]).first()
            topic_id = topic_record.id if topic_record else 1

            tp_obj = TeachingPair(
                group_id=group_obj.id,
                tutor_id=p["tutor_id"],
                learner_id=p["learner_id"],
                topic_id=topic_id,
                reason=p["reason"],
                status="recommended",
            )
            db.add(tp_obj)
            db.commit()
            db.refresh(tp_obj)

            teaching_pairs_out.append(PeerTeachingItem(
                id=tp_obj.id,
                tutor_id=p["tutor_id"],
                tutor_name=p["tutor_name"],
                learner_id=p["learner_id"],
                learner_name=p["learner_name"],
                topic_name=p["topic_name"],
                reason=p["reason"],
                status="recommended",
            ))

        # Calculate Common Schedules
        schedules_by_member: Dict[int, List[Dict[str, Any]]] = {}
        for sid in member_ids:
            sched_slots = db.query(StudySchedule).filter(
                StudySchedule.student_id == sid,
                StudySchedule.is_available == True
            ).all()
            schedules_by_member[sid] = [
                {"day_of_week": sl.day_of_week, "start_time": sl.start_time, "end_time": sl.end_time}
                for sl in sched_slots
            ]

        common_times = match_study_schedules(schedules_by_member, member_names)

        cov_metrics = g_data["coverage_metrics"]
        results.append(StudyGroupDetailOut(
            id=group_obj.id,
            name=group_obj.name,
            status=group_obj.status,
            member_count=len(members_summary),
            coverage_rate=cov_metrics["coverage_rate"],
            covered_topics=cov_metrics["covered_topics"],
            uncovered_topics=cov_metrics["uncovered_topics"],
            members=members_summary,
            teaching_pairs=teaching_pairs_out,
            common_schedules=common_times[:4], # top 4 sessions
            created_at=group_obj.created_at,
        ))

    return results


# ─────────────────────────────────────────────
# VIEW STUDY GROUPS
# ─────────────────────────────────────────────

@router.get("/groups", response_model=List[StudyGroupDetailOut])
def list_study_groups(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all active study groups with member profiles, coverage rates, and teaching pairs.
    """
    groups = (
        db.query(StudyGroup)
        .filter(StudyGroup.status == "active")
        .order_by(StudyGroup.name)
        .all()
    )
    results: List[StudyGroupDetailOut] = []

    for g in groups:
        members_summary: List[GroupMemberSummary] = []
        member_ids = []
        member_names = {}

        for gm in g.members:
            s = gm.student
            if not s:
                continue
            member_ids.append(s.id)
            member_names[s.id] = s.name
            skills = db.query(SkillProfile).filter(SkillProfile.student_id == s.id).all()
            members_summary.append(GroupMemberSummary(
                student_id=s.id,
                name=s.name,
                role=gm.role,
                strong_topics=[sp.topic for sp in skills if sp.status == "strong"],
                weak_topics=[sp.topic for sp in skills if sp.status == "weak"],
            ))

        # Re-compute coverage
        all_weak = set()
        all_strong = set()
        for m in members_summary:
            all_weak.update(m.weak_topics)
            all_strong.update(m.strong_topics)
        covered = sorted(list(all_weak.intersection(all_strong)))
        uncovered = sorted(list(all_weak - set(covered)))
        cov_rate = (len(covered) / max(len(all_weak), 1)) * 100.0 if all_weak else 100.0

        # Teaching Pairs
        teaching_pairs_out: List[PeerTeachingItem] = []
        for tp in g.teaching_pairs:
            teaching_pairs_out.append(PeerTeachingItem(
                id=tp.id,
                tutor_id=tp.tutor_id,
                tutor_name=tp.tutor.name if tp.tutor else "Tutor",
                learner_id=tp.learner_id,
                learner_name=tp.learner.name if tp.learner else "Learner",
                topic_name=tp.topic.name if tp.topic else "General",
                reason=tp.reason or "",
                status=tp.status or "recommended",
            ))

        # Common Schedules
        schedules_by_member = {}
        for sid in member_ids:
            sched_slots = db.query(StudySchedule).filter(
                StudySchedule.student_id == sid,
                StudySchedule.is_available == True
            ).all()
            schedules_by_member[sid] = [
                {"day_of_week": sl.day_of_week, "start_time": sl.start_time, "end_time": sl.end_time}
                for sl in sched_slots
            ]
        common_times = match_study_schedules(schedules_by_member, member_names)

        results.append(StudyGroupDetailOut(
            id=g.id,
            name=g.name,
            status=g.status,
            member_count=len(members_summary),
            coverage_rate=round(cov_rate, 2),
            covered_topics=covered,
            uncovered_topics=uncovered,
            members=members_summary,
            teaching_pairs=teaching_pairs_out,
            common_schedules=common_times[:4],
            created_at=g.created_at,
        ))

    return results


@router.get("/groups/my", response_model=Optional[StudyGroupDetailOut])
def get_my_study_group(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Student View: Returns the student's assigned study group, peer tutors,
    peers they can teach, and common study schedules.
    """
    membership = (
        db.query(GroupMember)
        .join(StudyGroup)
        .filter(
            GroupMember.student_id == current_user.id,
            StudyGroup.status == "active"
        )
        .first()
    )
    if not membership:
        return None

    group = membership.group
    all_groups = list_study_groups(current_user=current_user, db=db)
    for g_out in all_groups:
        if g_out.id == group.id:
            return g_out

    return None
