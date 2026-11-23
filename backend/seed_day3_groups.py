"""
StudyMatch AI - Day 3 Study Groups & Schedules Seed Script
Seeds student skill profiles and weekly study schedules across students.
"""
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Student, SkillProfile, StudySchedule, Subject, Topic

STUDENT_ARCHETYPES = {
    # Subject strengths/weaknesses distribution
    "Alex Morgan": {
        "strong": ["SQL Fundamentals", "Calculus & Limits", "Data Types & Collections"],
        "weak": ["Cell Biology & Mitosis", "Genetics & DNA"],
        "schedule": [("Monday", "17:00", "19:00"), ("Wednesday", "18:00", "20:00"), ("Saturday", "10:00", "12:00")]
    },
    "Rohit Sharma": {
        "strong": ["Object-Oriented Programming", "Variables & Expressions", "Table Joins"],
        "weak": ["Calculus & Limits", "Linear & Logistic Regression"],
        "schedule": [("Monday", "17:00", "19:00"), ("Wednesday", "18:00", "20:00"), ("Friday", "17:00", "19:00")]
    },
    "Arathy": {
        "strong": ["Cell Biology & Mitosis", "Plant Physiology", "Human Anatomy"],
        "weak": ["SQL Fundamentals", "Table Joins"],
        "schedule": [("Tuesday", "16:00", "18:00"), ("Thursday", "17:00", "19:00"), ("Saturday", "10:00", "12:00")]
    },
    "amaya": {
        "strong": ["Genetics & DNA", "Cell Biology & Mitosis", "Descriptive Statistics"],
        "weak": ["Object-Oriented Programming", "Variables & Expressions"],
        "schedule": [("Monday", "17:00", "19:00"), ("Tuesday", "16:00", "18:00"), ("Thursday", "17:00", "19:00")]
    },
    "arjun": {
        "strong": ["Linear & Logistic Regression", "Decision Trees & Ensembles", "Calculus & Limits"],
        "weak": ["Plant Physiology", "SQL Fundamentals"],
        "schedule": [("Monday", "17:00", "19:00"), ("Wednesday", "18:00", "20:00"), ("Saturday", "10:00", "12:00")]
    },
    "aryaindu": {
        "strong": ["Table Joins", "Subqueries & Nested Queries", "Object-Oriented Programming"],
        "weak": ["Linear Algebra & Matrices", "Calculus & Limits"],
        "schedule": [("Monday", "17:00", "19:00"), ("Thursday", "17:00", "19:00"), ("Friday", "17:00", "19:00")]
    }
}


def seed_day3_data():
    db = SessionLocal()
    print("--- Seeding Student Skill Profiles & Schedules (Day 3) ---")
    try:
        students = db.query(Student).filter(Student.role == "student").all()
        for s in students:
            # Find archetype by exact or partial name match
            archetype = None
            for name_key, data in STUDENT_ARCHETYPES.items():
                if name_key.lower() in s.name.lower():
                    archetype = data
                    break

            if not archetype:
                # Default complementary profile
                archetype = {
                    "strong": ["SQL Fundamentals", "Variables & Expressions"],
                    "weak": ["Calculus & Limits", "Cell Biology & Mitosis"],
                    "schedule": [("Monday", "17:00", "19:00"), ("Saturday", "10:00", "12:00")]
                }

            # 1. Seed/Update Skill Profiles
            for strong_topic in archetype["strong"]:
                entry = db.query(SkillProfile).filter(
                    SkillProfile.student_id == s.id,
                    SkillProfile.topic == strong_topic
                ).first()
                if not entry:
                    entry = SkillProfile(
                        student_id=s.id,
                        subject="Core Curriculum",
                        topic=strong_topic,
                        status="strong",
                        mastery_score=random.uniform(85.0, 98.0),
                        tests_taken=random.randint(2, 5),
                    )
                    db.add(entry)
                else:
                    entry.status = "strong"
                    entry.mastery_score = max(entry.mastery_score, 88.0)

            for weak_topic in archetype["weak"]:
                entry = db.query(SkillProfile).filter(
                    SkillProfile.student_id == s.id,
                    SkillProfile.topic == weak_topic
                ).first()
                if not entry:
                    entry = SkillProfile(
                        student_id=s.id,
                        subject="Core Curriculum",
                        topic=weak_topic,
                        status="weak",
                        mastery_score=random.uniform(25.0, 48.0),
                        tests_taken=random.randint(1, 3),
                    )
                    db.add(entry)
                else:
                    entry.status = "weak"
                    entry.mastery_score = min(entry.mastery_score, 45.0)

            # 2. Seed Weekly Study Schedules
            for day, start, end in archetype["schedule"]:
                sched = db.query(StudySchedule).filter(
                    StudySchedule.student_id == s.id,
                    StudySchedule.day_of_week == day,
                    StudySchedule.start_time == start
                ).first()
                if not sched:
                    sched = StudySchedule(
                        student_id=s.id,
                        day_of_week=day,
                        start_time=start,
                        end_time=end,
                        is_available=True,
                    )
                    db.add(sched)

        db.commit()
        print("✓ Successfully populated complementary SkillProfiles and StudySchedules for all students.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_day3_data()
