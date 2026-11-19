"""
READ-ONLY data audit for StudyMatch AI. Changes nothing in the database.
Run from the backend folder:  python audit_data.py
"""
import re
from collections import defaultdict

from sqlalchemy import func

from database import SessionLocal
from models import (
    Student, StudentProfile, Subject, Topic, Question, QuizAttempt,
    SkillProfile, StudyMaterial, StudyGroup, GroupMember, TeachingPair, StudySchedule,
)

TEST_EMAIL = re.compile(r"(@test\.com|@httptest\.com|day\d_|_test|example\.com)", re.I)
TEST_SUBJECT = re.compile(r"(^HTTP Subject|^QM Subject|^Blocked |Cloud Computing & DevOps)", re.I)


def norm(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def section(title):
    print("\n" + "=" * 64 + f"\n{title}\n" + "=" * 64)


def main():
    db = SessionLocal()
    try:
        section("1. Row counts")
        for model in (Student, StudentProfile, Subject, Topic, Question, QuizAttempt,
                      SkillProfile, StudyMaterial, StudyGroup, GroupMember,
                      TeachingPair, StudySchedule):
            print(f"{model.__tablename__:20s} {db.query(model).count()}")

        section("2. Duplicate subjects (same name ignoring case/spaces)")
        groups = defaultdict(list)
        for s in db.query(Subject).all():
            groups[norm(s.name)].append(s)
        found = False
        for name, items in groups.items():
            if len(items) > 1:
                found = True
                print(f"'{name}': ids {[s.id for s in items]}")
        print("None" if not found else "")

        section("3. Duplicate topics (same subject + same name)")
        groups = defaultdict(list)
        for t in db.query(Topic).all():
            groups[(t.subject_id, norm(t.name))].append(t)
        found = False
        for (sid, name), items in groups.items():
            if len(items) > 1:
                found = True
                print(f"subject {sid} topic '{name}': ids {[t.id for t in items]}")
        print("None" if not found else "")

        section("4. Duplicate questions (same topic + same text)")
        groups = defaultdict(list)
        for q in db.query(Question).all():
            groups[(q.topic_id, norm(q.question_text))].append(q)
        found = False
        for (tid, text), items in groups.items():
            if len(items) > 1:
                found = True
                print(f"topic {tid}: {len(items)} copies (ids {[q.id for q in items]}) '{text[:60]}'")
        print("None" if not found else "")

        section("5. Duplicate study materials (same title + subject + topic)")
        groups = defaultdict(list)
        for m in db.query(StudyMaterial).all():
            groups[(norm(m.title), norm(m.subject), norm(m.topic))].append(m)
        found = False
        for key, items in groups.items():
            if len(items) > 1:
                found = True
                print(f"{len(items)} copies (ids {[m.id for m in items]}) '{key[0][:60]}'")
        print("None" if not found else "")

        section("6. Duplicate study groups / schedules / teaching pairs")
        names = db.query(StudyGroup.name, func.count()).group_by(StudyGroup.name).having(func.count() > 1).all()
        print("Groups with the same name:", names or "None")
        print("Study groups in total:", db.query(StudyGroup).count(),
              "(regenerating groups should replace old ones)")
        dup_slots = (db.query(StudySchedule.student_id, StudySchedule.day_of_week,
                              StudySchedule.start_time, StudySchedule.end_time, func.count())
                     .group_by(StudySchedule.student_id, StudySchedule.day_of_week,
                               StudySchedule.start_time, StudySchedule.end_time)
                     .having(func.count() > 1).all())
        print("Duplicate schedule slots:", dup_slots or "None")
        dup_pairs = (db.query(TeachingPair.group_id, TeachingPair.tutor_id,
                              TeachingPair.learner_id, TeachingPair.topic_id, func.count())
                     .group_by(TeachingPair.group_id, TeachingPair.tutor_id,
                               TeachingPair.learner_id, TeachingPair.topic_id)
                     .having(func.count() > 1).all())
        print("Duplicate teaching pairs:", dup_pairs or "None")

        section("7. Students with no course set, or the placeholder 'General'")
        no_course = (db.query(Student.id, Student.name, Student.email, StudentProfile.course)
                     .outerjoin(StudentProfile, StudentProfile.student_id == Student.id)
                     .filter(Student.role == "student")
                     .filter((StudentProfile.course.is_(None)) | (func.lower(StudentProfile.course) == "general"))
                     .all())
        print(f"{len(no_course)} student(s)")
        for row in no_course[:15]:
            print("  ", tuple(row))

        section("8. Distinct courses currently on student profiles")
        for course, n in (db.query(StudentProfile.course, func.count())
                          .group_by(StudentProfile.course).order_by(func.count().desc()).all()):
            print(f"  {n:3d}  {course!r}")

        section("9. Suspected TEST / leftover data (review before deleting)")
        print("Test-looking accounts:")
        for s in db.query(Student).all():
            if TEST_EMAIL.search(s.email or ""):
                print(f"  id {s.id}  {s.role:8s} {s.email}")
        print("Test-looking subjects:")
        for s in db.query(Subject).all():
            if TEST_SUBJECT.search(s.name or ""):
                print(f"  id {s.id}  {s.name}")
        print("Questions identical to the one test_day2.py adds on every run:")
        n = db.query(Question).filter(Question.question_text.ilike("What does DML stand for%")).count()
        print(f"  {n} copies")

        print("\nAudit finished. Nothing was changed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()