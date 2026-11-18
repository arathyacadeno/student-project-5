import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student", nullable=False) # 'student' or 'teacher'

    profile = relationship("StudentProfile", back_populates="student", uselist=False, cascade="all, delete-orphan")
    skills = relationship("SkillProfile", back_populates="student", cascade="all, delete-orphan")
    bookmarks = relationship("MaterialBookmark", back_populates="student", cascade="all, delete-orphan")
    mock_tests = relationship("MockTest", back_populates="student", cascade="all, delete-orphan")
    paper_attempts = relationship("PaperAttempt", back_populates="student", cascade="all, delete-orphan")
    mentor_messages = relationship("MentorChatMessage", back_populates="student", cascade="all, delete-orphan")
    interest_profile = relationship("InterestProfile", back_populates="student", uselist=False, cascade="all, delete-orphan")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    course = Column(String(100))
    stream = Column(String(100))
    academic_level = Column(String(50))
    learning_goal = Column(String(255))

    student = relationship("Student", back_populates="profile")


class SkillProfile(Base):
    __tablename__ = "skill_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(100), nullable=False)
    status = Column(String(20), default="average", nullable=False) # 'weak', 'average', 'strong'
    mastery_score = Column(Float, default=50.0) # 0 to 100
    tests_taken = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "subject", "topic", name="uq_student_subject_topic"),
    )

    student = relationship("Student", back_populates="skills")


class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    material_type = Column(String(50), nullable=False) # 'notes', 'learning_material', 'important_questions', 'topic_resource'
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    difficulty_level = Column(String(20), default="medium") # 'easy', 'medium', 'difficult'
    uploaded_by = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    uploader = relationship("Student", foreign_keys=[uploaded_by])
    bookmarks = relationship("MaterialBookmark", back_populates="material", cascade="all, delete-orphan")


class MaterialBookmark(Base):
    __tablename__ = "material_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("study_materials.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "material_id", name="uq_student_material_bookmark"),
    )

    student = relationship("Student", back_populates="bookmarks")
    material = relationship("StudyMaterial", back_populates="bookmarks")


class QuestionBank(Base):
    __tablename__ = "question_bank"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    difficulty = Column(String(20), nullable=False, index=True) # 'easy', 'medium', 'difficult'
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False) # ["Option A", "Option B", "Option C", "Option D"]
    correct_option = Column(Integer, nullable=False) # 0, 1, 2, 3
    explanation = Column(Text, nullable=True)
    related_material_id = Column(Integer, ForeignKey("study_materials.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    related_material = relationship("StudyMaterial")


class MockTest(Base):
    __tablename__ = "mock_tests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(100), nullable=False)
    difficulty_mode = Column(String(20), nullable=False) # 'adaptive', 'easy', 'medium', 'difficult'
    time_limit_minutes = Column(Integer, default=15)
    total_questions = Column(Integer, default=10)
    score = Column(Float, default=0.0)
    total_marks = Column(Integer, default=10)
    status = Column(String(20), default="in_progress") # 'in_progress', 'completed'
    topic_breakdown = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="mock_tests")
    responses = relationship("MockTestResponse", back_populates="mock_test", cascade="all, delete-orphan")


class MockTestResponse(Base):
    __tablename__ = "mock_test_responses"

    id = Column(Integer, primary_key=True, index=True)
    mock_test_id = Column(Integer, ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("question_bank.id", ondelete="CASCADE"), nullable=False)
    selected_option = Column(Integer, nullable=True) # None if skipped
    is_correct = Column(Boolean, default=False)
    topic = Column(String(100), nullable=False)

    mock_test = relationship("MockTest", back_populates="responses")
    question = relationship("QuestionBank")


class PreviousPaper(Base):
    __tablename__ = "previous_papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    time_limit_minutes = Column(Integer, default=60)
    total_marks = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    questions = relationship("PaperQuestion", back_populates="paper", cascade="all, delete-orphan")
    attempts = relationship("PaperAttempt", back_populates="paper", cascade="all, delete-orphan")


class PaperQuestion(Base):
    __tablename__ = "paper_questions"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("previous_papers.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    topic = Column(String(100), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_option = Column(Integer, nullable=False)
    step_by_step_solution = Column(Text, nullable=False)
    related_material_id = Column(Integer, ForeignKey("study_materials.id", ondelete="SET NULL"), nullable=True)

    paper = relationship("PreviousPaper", back_populates="questions")
    related_material = relationship("StudyMaterial")


class PaperAttempt(Base):
    __tablename__ = "paper_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    paper_id = Column(Integer, ForeignKey("previous_papers.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    total_marks = Column(Integer, nullable=False)
    time_spent_seconds = Column(Integer, default=0)
    answers = Column(JSON, nullable=False) # {"question_id": {"selected": 2, "is_correct": true}}
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="paper_attempts")
    paper = relationship("PreviousPaper", back_populates="attempts")


class GuidanceCourse(Base):
    __tablename__ = "guidance_courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    stream = Column(String(100), nullable=False)
    degree_level = Column(String(50), nullable=False) # 'Undergraduate', 'Postgraduate', 'Integrated'
    description = Column(Text, nullable=False)
    eligibility = Column(Text, nullable=False)
    fees_range = Column(String(100), nullable=False)
    scope_and_careers = Column(JSON, nullable=False) # list of career strings
    entrance_exams = Column(JSON, nullable=False) # list of exam objects with dates/details
    roadmap_steps = Column(JSON, nullable=False) # list of roadmap step objects {stage, title, description}
    matching_tags = Column(JSON, nullable=False) # list of topic/interest keywords for ML scoring


class InterestProfile(Base):
    __tablename__ = "interest_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    answers = Column(JSON, nullable=False) # raw questionnaire answers
    interest_tags = Column(JSON, nullable=False) # extracted interest tags
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="interest_profile")


class CourseSummary(Base):
    __tablename__ = "course_summaries"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    overview = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=False) # list of key bullet point strings
    quick_revision_notes = Column(Text, nullable=False)
    quiz_questions = Column(JSON, nullable=False) # list of {question, options, correct_option, explanation}
    is_ai_generated = Column(Boolean, default=False)
    last_edited_by = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    editor = relationship("Student")


class MentorChatMessage(Base):
    __tablename__ = "mentor_chat_history"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False) # 'student' or 'mentor'
    message = Column(Text, nullable=False)
    referenced_topics = Column(JSON, nullable=True) # list of weak/strong topics mentioned
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="mentor_messages")
