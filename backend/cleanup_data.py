"""
StudyMatch AI - data cleanup.

DRY RUN by default: prints exactly what would be deleted and changes nothing.
    python cleanup_data.py
To really delete (asks you to type 'yes' first):
    python cleanup_data.py --apply
To also delete specific duplicate accounts you have chosen (by id):
    python cleanup_data.py --apply --delete-student-ids 2,5,8
"""
import argparse
import re
import sys
from collections import defaultdict

from sqlalchemy import text

from database import SessionLocal
from models import Student, Subject, Question

TEST_EMAIL = re.compile(r"(@test\.com|@httptest\.com)$", re.I)
TEST_SUBJECT = re.compile(r"(^HTTP Subject|^QM Subject|^Blocked |^Cloud Computing & DevOps$)", re.I)


def norm(t):
    return (t or "").strip().lower()


def build_plan(db, extra_student_ids):
    plan = {"questions": [], "students": [], "subjects": []}

    # 1. Duplicate questions: keep the oldest copy, delete the rest
    groups = defaultdict(list)
    for q in db.query(Question).order_by(Question.id).all():
        groups[(q.topic_id, norm(q.question_text))].append(q)
    for items in groups.values():
        plan["questions"].extend(items[1:])

    # 2. Test accounts (only clearly test-pattern emails) + accounts you chose by id
    wanted = set(extra_student_ids)
    for s in db.query(Student).all():
        if TEST_EMAIL.search(s.email or "") or s.id in wanted:
            plan["students"].append(s)

    # 3. Test subjects (their topics and questions are deleted with them)
    for s in db.query(Subject).all():
        if TEST_SUBJECT.search(s.name or ""):
            plan["subjects"].append(s)
    return plan


def print_plan(plan):
    print("\nWould delete:")
    print(f"\n  Duplicate questions ({len(plan['questions'])}):")
    for q in plan["questions"]:
        print(f"    id {q.id} (topic {q.topic_id}): {q.question_text[:70]}")
    print(f"\n  Accounts ({len(plan['students'])})  [their quiz data, profiles, groups etc. go too]:")
    for s in plan["students"]:
        print(f"    id {s.id} {s.role:8s} {s.name} <{s.email}>")
    print(f"\n  Subjects ({len(plan['subjects'])})  [with all their topics and questions]:")
    for s in plan["subjects"]:
        print(f"    id {s.id} {s.name} ({len(s.topics)} topic(s))")
    total = len(plan["questions"]) + len(plan["students"]) + len(plan["subjects"])
    return total


def add_unique_indexes(db):
    """Stop duplicates from coming back, at database level."""
    statements = [
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_topic_subject_name ON topics (subject_id, lower(name))",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_question_topic_text "
        "ON questions (topic_id, md5(lower(trim(question_text))))",
    ]
    for stmt in statements:
        try:
            db.execute(text(stmt))
            db.commit()
            print("  ✓", stmt.split(" ON ")[0])
        except Exception as exc:
            db.rollback()
            print("  ✗ could not create index:", str(exc).splitlines()[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--delete-student-ids", default="")
    args = parser.parse_args()
    extra = [int(x) for x in args.delete_student_ids.split(",") if x.strip().isdigit()]

    db = SessionLocal()
    try:
        plan = build_plan(db, extra)
        total = print_plan(plan)
        if total == 0:
            print("\nNothing to delete.")
        if not args.apply:
            print("\nDRY RUN - nothing was changed. Add --apply to delete.")
            return
        if total and input("\nType 'yes' to delete the items above: ").strip().lower() != "yes":
            print("Cancelled. Nothing was changed.")
            sys.exit(0)

        # Subjects first (cascades to topics/questions), then leftover questions, then accounts
        for s in plan["subjects"]:
            db.delete(s)
        db.commit()
        for q in plan["questions"]:
            obj = db.get(Question, q.id)
            if obj:
                db.delete(obj)
        db.commit()
        for s in plan["students"]:
            obj = db.get(Student, s.id)
            if obj:
                db.delete(obj)
        db.commit()
        print("\n✓ Deleted.")
        print("\nAdding database rules that prevent duplicates:")
        add_unique_indexes(db)
        print("\nNext: regenerate study groups from the Teacher Dashboard "
              "(deleted accounts may have left groups too small).")
    finally:
        db.close()


if __name__ == "__main__":
    main()