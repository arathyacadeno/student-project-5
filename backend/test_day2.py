"""
Unit & Integration Test Suite for Day 2: Quiz & Machine Learning
Tests ML Random Forest Classifier, Joblib serialization, Quiz grading, and Skill Profile auto-update.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Student, Topic, Question, SkillProfile, QuizAttempt
from ml.predictor import predict_topic_strength
from routers import quiz as quiz_router


def run_day2_tests():
    db = SessionLocal()
    print("--- Starting Day 2 Quiz & Machine Learning Tests ---")

    try:
        # 1. Test ML Inference on Pre-trained Random Forest Model
        print("[ML Random Forest Engine]")
        weak_res = predict_topic_strength(score_pct=25.0, correct_answers=1, incorrect_answers=3)
        assert weak_res["predicted_status"] == "weak"
        print(f"  ✓ Weak classification verified: {weak_res['predicted_status']} (Confidence: {weak_res['confidence']}%)")

        avg_res = predict_topic_strength(score_pct=60.0, correct_answers=3, incorrect_answers=2)
        assert avg_res["predicted_status"] == "average"
        print(f"  ✓ Average classification verified: {avg_res['predicted_status']} (Confidence: {avg_res['confidence']}%)")

        strong_res = predict_topic_strength(score_pct=100.0, correct_answers=4, incorrect_answers=0)
        assert strong_res["predicted_status"] == "strong"
        print(f"  ✓ Strong classification verified: {strong_res['predicted_status']} (Confidence: {strong_res['confidence']}%)")

        # 2. Test Direct ML API Endpoint Schema
        ml_req = quiz_router.MLPredictRequest(
            score_pct=95.0,
            correct_answers=10,
            incorrect_answers=0,
            avg_time_per_q=22.0
        )
        api_ml_res = quiz_router.predict_topic_strength_api(ml_req)
        assert api_ml_res["predicted_status"] == "strong"
        print("  ✓ Public ML Inference API (/api/v1/ml/predict-strength) verified.")

        # 3. Test Teacher Question Creation
        print("\n[Teacher Question Management]")
        teacher = db.query(Student).filter(Student.role == "teacher").first()
        topic = db.query(Topic).filter(Topic.name == "SQL Fundamentals").first()
        assert topic is not None, "Topic 'SQL Fundamentals' must exist."

        q_create_req = quiz_router.QuestionCreate(
            topic_id=topic.id,
            question_text="What does DML stand for in Database Systems?",
            options=[
                "Data Manipulation Language",
                "Data Modification Level",
                "Dynamic Management Layer",
                "Direct Memory Link"
            ],
            correct_answer=0,
            explanation="DML stands for Data Manipulation Language (SELECT, INSERT, UPDATE, DELETE).",
            difficulty="easy"
        )
        new_q = quiz_router.add_quiz_question(req=q_create_req, current_user=teacher, db=db)
        assert new_q.id is not None
        assert new_q.correct_answer == 0
        print(f"  ✓ Teacher added diagnostic question to '{topic.name}' (ID: {new_q.id}).")

        # 4. Student Fetches Quiz (Verify Answers are Hidden)
        print("\n[Student Diagnostic Quiz & Evaluation]")
        student = db.query(Student).filter(Student.role == "student").first()
        assert student is not None, "A student user must exist."

        quiz_data = quiz_router.get_topic_quiz(topic_id=topic.id, current_user=student, db=db)
        assert quiz_data.total_questions >= 1
        # Check that QuestionPublic does NOT leak correct_answer attribute to the student
        for q in quiz_data.questions:
            assert not hasattr(q, "correct_answer") or getattr(q, "correct_answer", None) is None
        print(f"  ✓ Retrieved {quiz_data.total_questions} questions for '{topic.name}'. Verified answers are masked from student.")

        # 5. Student Submits Quiz with WEAK answers (e.g. all wrong)
        wrong_answers = {q.id: (q.options.index(q.options[0]) + 1) % len(q.options) for q in quiz_data.questions}
        sub_req = quiz_router.QuizSubmitRequest(answers=wrong_answers, time_taken_sec=45)
        eval_result = quiz_router.submit_topic_quiz(
            topic_id=topic.id,
            req=sub_req,
            current_user=student,
            db=db
        )
        assert eval_result.attempt_id is not None
        assert eval_result.predicted_status == "weak"
        print(f"  ✓ Weak submission graded: Accuracy {eval_result.accuracy}%, ML status: {eval_result.predicted_status}")

        # Check SkillProfile in DB auto-updated to 'weak'
        skill_entry = (
            db.query(SkillProfile)
            .filter(SkillProfile.student_id == student.id, SkillProfile.topic == topic.name)
            .first()
        )
        assert skill_entry is not None
        assert skill_entry.status == "weak"
        print(f"  ✓ SkillProfile in DB auto-updated to: status='{skill_entry.status}', tests_taken={skill_entry.tests_taken}")

        # 6. Student Retakes and Submits PERFECT answers
        # Query true correct answers from DB
        db_questions = db.query(Question).filter(Question.topic_id == topic.id).all()
        correct_answers = {q.id: q.correct_answer for q in db_questions}
        sub_req_perfect = quiz_router.QuizSubmitRequest(answers=correct_answers, time_taken_sec=25)
        eval_result_perfect = quiz_router.submit_topic_quiz(
            topic_id=topic.id,
            req=sub_req_perfect,
            current_user=student,
            db=db
        )
        assert eval_result_perfect.accuracy == 100.0
        assert eval_result_perfect.predicted_status == "strong"
        print(f"  ✓ Perfect submission graded: Accuracy {eval_result_perfect.accuracy}%, ML status: {eval_result_perfect.predicted_status}")

        # Check SkillProfile in DB auto-promoted to 'strong'
        db.refresh(skill_entry)
        assert skill_entry.status == "strong"
        print(f"  ✓ SkillProfile in DB successfully promoted to: status='{skill_entry.status}'!")

        # 7. Student Views Quiz Attempts History
        attempts = quiz_router.get_my_quiz_attempts(current_user=student, db=db)
        assert len(attempts) >= 2
        print(f"  ✓ Student quiz history fetched ({len(attempts)} attempts logged).")

        print("\n=======================================================")
        print("🎉 ALL DAY 2 QUIZ & MACHINE LEARNING TESTS PASSED! 🎉")
        print("=======================================================\n")

    finally:
        db.close()


if __name__ == "__main__":
    run_day2_tests()
