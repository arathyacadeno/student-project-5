import datetime
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Subject,
    Topic,
    Question,
    QuizAttempt,
    QuizAnswer,
    TopicPerformance,
    SkillProfile,
    Student,
)
from auth import get_current_user, require_teacher, require_student
from ml.predictor import predict_topic_strength

router = APIRouter()


# ─────────────────────────────────────────────
# PYDANTIC SCHEMAS
# ─────────────────────────────────────────────

class QuestionCreate(BaseModel):
    topic_id: int
    question_text: str
    options: List[str] = Field(..., min_items=2, max_items=6)
    correct_answer: int = Field(..., ge=0, le=5)
    explanation: Optional[str] = None
    difficulty: Optional[str] = "medium"


class QuestionPublic(BaseModel):
    id: int
    topic_id: int
    question_text: str
    options: List[str]
    difficulty: Optional[str] = "medium"

    class Config:
        from_attributes = True


class QuestionDetailOut(QuestionPublic):
    correct_answer: int
    explanation: Optional[str] = None


class TopicQuizResponse(BaseModel):
    topic_id: int
    topic_name: str
    subject_id: int
    subject_name: str
    total_questions: int
    questions: List[QuestionPublic]


class QuizSubmitRequest(BaseModel):
    answers: Dict[int, int] # { question_id: selected_option_index }
    time_taken_sec: Optional[int] = 60


class QuestionResultItem(BaseModel):
    question_id: int
    question_text: str
    options: List[str]
    selected_option: int
    correct_answer: int
    is_correct: bool
    explanation: Optional[str] = None


class QuizResultResponse(BaseModel):
    attempt_id: int
    student_id: int
    topic_id: int
    topic_name: str
    subject_name: str
    score: float
    total_marks: float
    accuracy: float
    time_taken_sec: int
    # ML Classification Output
    predicted_status: str # 'weak', 'average', 'strong'
    ml_confidence: float
    probabilities: Dict[str, float]
    # Detailed Breakdown
    correct_count: int
    incorrect_count: int
    questions_breakdown: List[QuestionResultItem]
    created_at: datetime.datetime


class MLPredictRequest(BaseModel):
    score_pct: float = Field(..., ge=0, le=100)
    correct_answers: int = Field(..., ge=0)
    incorrect_answers: int = Field(..., ge=0)
    avg_time_per_q: Optional[float] = 45.0
    attempt_number: Optional[int] = 1
    historical_accuracy: Optional[float] = None


# ─────────────────────────────────────────────
# QUESTION MANAGEMENT (TEACHER)
# ─────────────────────────────────────────────

@router.post("/quiz/questions", response_model=QuestionDetailOut, status_code=status.HTTP_201_CREATED)
def add_quiz_question(
    req: QuestionCreate,
    current_user: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Teacher Only: Add a new multiple-choice diagnostic question to a topic.
    """
    topic = db.query(Topic).filter(Topic.id == req.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with ID {req.topic_id} does not exist.",
        )

    if req.correct_answer >= len(req.options):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"correct_answer index ({req.correct_answer}) exceeds options length ({len(req.options)}).",
        )

    q = Question(
        topic_id=req.topic_id,
        question_text=req.question_text.strip(),
        options=req.options,
        correct_answer=req.correct_answer,
        explanation=req.explanation.strip() if req.explanation else None,
        difficulty=req.difficulty or "medium",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@router.get("/quiz/questions", response_model=List[QuestionDetailOut])
def list_questions(
    topic_id: Optional[int] = None,
    current_user: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Teacher Only: View question bank with answers and explanations.
    """
    query = db.query(Question)
    if topic_id:
        query = query.filter(Question.topic_id == topic_id)
    return query.order_by(Question.id).all()


# ─────────────────────────────────────────────
# STUDENT DIAGNOSTIC QUIZ
# ─────────────────────────────────────────────

@router.get("/quiz/topic/{topic_id}", response_model=TopicQuizResponse)
def get_topic_quiz(
    topic_id: int,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch diagnostic quiz for a topic.
    Answers and explanations are stripped so student cannot peek.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found.")

    questions = db.query(Question).filter(Question.topic_id == topic_id).all()
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No questions are currently available for topic '{topic.name}'.",
        )

    return TopicQuizResponse(
        topic_id=topic.id,
        topic_name=topic.name,
        subject_id=topic.subject.id,
        subject_name=topic.subject.name,
        total_questions=len(questions),
        questions=[QuestionPublic.from_orm(q) for q in questions],
    )


@router.post("/quiz/topic/{topic_id}/submit", response_model=QuizResultResponse)
def submit_topic_quiz(
    topic_id: int,
    req: QuizSubmitRequest,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit diagnostic quiz answers:
      1. Automatically evaluates answers and computes accuracy.
      2. Records QuizAttempt and individual QuizAnswer entries.
      3. Predicts topic mastery ('weak', 'average', 'strong') using trained Random Forest ML.
      4. Auto-updates student's SkillProfile and TopicPerformance.
      5. Returns full results breakdown with explanations.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found.")

    questions = db.query(Question).filter(Question.topic_id == topic_id).all()
    if not questions:
        raise HTTPException(status_code=400, detail="Topic has no questions to evaluate.")

    total_q = len(questions)
    correct_count = 0
    breakdown: List[QuestionResultItem] = []

    # Calculate question by question
    for q in questions:
        selected_opt = req.answers.get(q.id, -1)
        is_corr = (selected_opt == q.correct_answer)
        if is_corr:
            correct_count += 1

        breakdown.append(QuestionResultItem(
            question_id=q.id,
            question_text=q.question_text,
            options=q.options,
            selected_option=selected_opt,
            correct_answer=q.correct_answer,
            is_correct=is_corr,
            explanation=q.explanation,
        ))

    score = float(correct_count)
    total_marks = float(total_q)
    accuracy_pct = round((score / total_marks) * 100.0, 2)
    incorrect_count = total_q - correct_count
    time_taken = max(req.time_taken_sec or 30, 5)
    avg_time_per_q = round(time_taken / max(total_q, 1), 2)

    # 1. Create QuizAttempt record
    attempt = QuizAttempt(
        student_id=current_user.id,
        topic_id=topic_id,
        score=score,
        total_marks=total_marks,
        accuracy=accuracy_pct,
        time_taken_sec=time_taken,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # 2. Record individual QuizAnswer items
    for item in breakdown:
        ans_record = QuizAnswer(
            attempt_id=attempt.id,
            question_id=item.question_id,
            selected_option=item.selected_option,
            is_correct=item.is_correct,
        )
        db.add(ans_record)
    db.commit()

    # 3. Retrieve historical performance on this topic
    prior_attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.student_id == current_user.id, QuizAttempt.topic_id == topic_id)
        .all()
    )
    attempt_num = len(prior_attempts)
    hist_acc = sum(a.accuracy for a in prior_attempts) / max(attempt_num, 1)

    # 4. Predict Topic Strength using Random Forest Model
    ml_output = predict_topic_strength(
        score_pct=accuracy_pct,
        correct_answers=correct_count,
        incorrect_answers=incorrect_count,
        avg_time_per_q=avg_time_per_q,
        attempt_number=attempt_num,
        historical_accuracy=round(hist_acc, 2),
    )
    predicted_status = ml_output["predicted_status"]
    ml_confidence = ml_output["confidence"]
    probabilities = ml_output["probabilities"]

    # 5. Update TopicPerformance table
    perf = (
        db.query(TopicPerformance)
        .filter(TopicPerformance.student_id == current_user.id, TopicPerformance.topic_id == topic_id)
        .first()
    )
    if not perf:
        perf = TopicPerformance(
            student_id=current_user.id,
            topic_id=topic_id,
            accuracy=accuracy_pct,
            attempt_count=attempt_num,
            status=predicted_status,
        )
        db.add(perf)
    else:
        perf.accuracy = round((perf.accuracy + accuracy_pct) / 2.0, 2)
        perf.attempt_count = attempt_num
        perf.status = predicted_status
        perf.last_attempt_date = datetime.datetime.utcnow()
    db.commit()

    # 6. Upsert SkillProfile for Intelligent Study Group Matcher (Module 6 & 7)
    skill_entry = (
        db.query(SkillProfile)
        .filter(
            SkillProfile.student_id == current_user.id,
            SkillProfile.topic == topic.name
        )
        .first()
    )
    if not skill_entry:
        skill_entry = SkillProfile(
            student_id=current_user.id,
            subject=topic.subject.name,
            topic=topic.name,
            status=predicted_status,
            mastery_score=accuracy_pct,
            tests_taken=attempt_num,
            updated_at=datetime.datetime.utcnow(),
        )
        db.add(skill_entry)
    else:
        skill_entry.status = predicted_status
        skill_entry.mastery_score = accuracy_pct
        skill_entry.tests_taken += 1
        skill_entry.updated_at = datetime.datetime.utcnow()
    db.commit()

    return QuizResultResponse(
        attempt_id=attempt.id,
        student_id=current_user.id,
        topic_id=topic.id,
        topic_name=topic.name,
        subject_name=topic.subject.name,
        score=score,
        total_marks=total_marks,
        accuracy=accuracy_pct,
        time_taken_sec=time_taken,
        predicted_status=predicted_status,
        ml_confidence=ml_confidence,
        probabilities=probabilities,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        questions_breakdown=breakdown,
        created_at=attempt.created_at,
    )


@router.get("/quiz/attempts/my", response_model=List[Dict[str, Any]])
def get_my_quiz_attempts(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all diagnostic quiz attempts for current student.
    """
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.student_id == current_user.id)
        .order_by(QuizAttempt.created_at.desc())
        .all()
    )
    results = []
    for a in attempts:
        results.append({
            "attempt_id": a.id,
            "topic_id": a.topic_id,
            "topic_name": a.topic.name if a.topic else "Unknown Topic",
            "subject_name": a.topic.subject.name if (a.topic and a.topic.subject) else "General",
            "score": a.score,
            "total_marks": a.total_marks,
            "accuracy": a.accuracy,
            "time_taken_sec": a.time_taken_sec,
            "created_at": a.created_at.isoformat(),
        })
    return results


# ─────────────────────────────────────────────
# DIRECT ML PREDICTION API
# ─────────────────────────────────────────────

@router.post("/ml/predict-strength")
def predict_topic_strength_api(req: MLPredictRequest):
    """
    Public ML Inference Endpoint:
    Accepts student quiz metrics and outputs predicted topic mastery classification
    ('weak', 'average', 'strong') with confidence and class probabilities.
    """
    return predict_topic_strength(
        score_pct=req.score_pct,
        correct_answers=req.correct_answers,
        incorrect_answers=req.incorrect_answers,
        avg_time_per_q=req.avg_time_per_q if req.avg_time_per_q is not None else 45.0,
        attempt_number=req.attempt_number or 1,
        historical_accuracy=req.historical_accuracy,
    )

@router.delete("/quiz/questions/{question_id}")
def delete_quiz_question(
    question_id: int,
    current_user: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Teacher Only: Delete a quiz question (students' stored answers to it are removed too).
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")
    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully."}