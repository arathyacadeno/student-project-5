"""
Test suite for Phase 1: Modules 4, 5, and 6 Endpoints
Direct Python invocation matching test_api.py style.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Student, Course, Test, TestAttempt, ChatSession
from routers.guidance import (
    get_roadmap, list_exams, get_exam, list_colleges,
    list_courses, recommend_courses, compare_courses, career_path,
    list_scholarships, list_study_abroad, add_checklist_item, get_checklist,
    update_checklist_item, create_counselling_request, get_counselling_requests,
    update_counselling_request
)
from routers.mock_tests_v2 import (
    list_papers, list_tests, get_test, start_test_attempt,
    submit_test_attempt, get_attempt_result, generate_adaptive_test
)
from routers.chatbot import (
    list_documents, create_session, list_sessions, send_message, get_messages
)

def run_tests():
    print("--- Starting Phase 1 Integration Tests (Modules 4, 5, 6) ---")
    db = SessionLocal()

    student = db.query(Student).filter(Student.email == "student@studymatch.ai").first()
    teacher = db.query(Student).filter(Student.email == "teacher@studymatch.ai").first()
    assert student is not None, "Student user not found in database"
    assert teacher is not None, "Teacher user not found in database"

    # ─────────────────────────────────────────
    # MODULE 4: GUIDANCE
    # ─────────────────────────────────────────
    print("\n[Module 4] Higher Studies & Guidance Tests:")

    # 1. Roadmap
    roadmap = get_roadmap(stream=None, db=db, current_user=student)
    assert len(roadmap) >= 3, f"Expected >= 3 roadmap stages, got {len(roadmap)}"
    print(f"  ✓ Roadmap stages retrieved: {len(roadmap)} stages")

    # 2. Entrance exams
    exams = list_exams(stream=None, search=None, skip=0, limit=50, db=db, current_user=student)
    assert exams["total"] >= 5, f"Expected >= 5 exams, got {exams['total']}"
    exam_id = exams["items"][0]["id"]
    exam_detail = get_exam(exam_id=exam_id, db=db, current_user=student)
    assert "syllabus" in exam_detail
    print(f"  ✓ Exams list & detail: {exams['total']} exams available (Sample: {exam_detail['name']})")

    # 3. Colleges
    colleges = list_colleges(state=None, college_type=None, search=None, skip=0, limit=30, db=db, current_user=student)
    assert colleges["total"] >= 5
    print(f"  ✓ Colleges list: {colleges['total']} colleges indexed")

    # 4. Courses & Recommendations
    courses = list_courses(stream=None, degree_level=None, search=None, skip=0, limit=30, db=db, current_user=student)
    assert courses["total"] >= 8
    c1, c2 = courses["items"][0]["id"], courses["items"][1]["id"]

    rec_list = recommend_courses(db=db, current_user=student)
    assert len(rec_list) > 0
    assert "match_score" in rec_list[0]
    print(f"  ✓ ML Course Recommendations: Top choice '{rec_list[0]['title']}' (Score: {rec_list[0]['match_score']}%, Reason: {rec_list[0]['match_reason']})")

    # Compare courses
    cmp_res = compare_courses(ids=f"{c1},{c2}", db=db, current_user=student)
    assert len(cmp_res["courses"]) == 2
    print(f"  ✓ Course Comparison: Comparing '{cmp_res['courses'][0]['title']}' vs '{cmp_res['courses'][1]['title']}'")

    # Career path
    cp_res = career_path(course_id=c1, db=db, current_user=student)
    assert "growth_path" in cp_res
    print(f"  ✓ Career Path Explorer: {len(cp_res['job_roles'])} target roles for {cp_res['course_title']}")

    # 5. Scholarships & Study Abroad
    sch_res = list_scholarships(category=None, search=None, skip=0, limit=30, db=db, current_user=student)
    assert sch_res["total"] >= 4
    sa_res = list_study_abroad(db=db, current_user=student)
    assert len(sa_res) >= 4
    print(f"  ✓ Scholarships ({sch_res['total']}) & Study Abroad ({len(sa_res)} countries)")

    # 6. Checklist
    add_cl = add_checklist_item({"title": "Submit JEE Form", "category": "Exam"}, db=db, current_user=student)
    cl_id = add_cl["id"]
    cl_items = get_checklist(db=db, current_user=student)
    assert any(i["id"] == cl_id for i in cl_items)
    update_checklist_item(item_id=cl_id, payload={"is_completed": True}, db=db, current_user=student)
    print("  ✓ Application Checklist CRUD operational")

    # 7. Counselling requests
    couns_add = create_counselling_request({"message": "I need help deciding between CSE and ECE.", "preferred_mode": "Online"}, db=db, current_user=student)
    couns_id = couns_add["id"]
    tch_couns = get_counselling_requests(status_filter=None, db=db, current_user=teacher)
    assert any(c["id"] == couns_id for c in tch_couns)
    update_counselling_request(req_id=couns_id, payload={"status": "scheduled", "teacher_notes": "Session booked for Friday 4pm"}, db=db, current_user=teacher)
    print("  ✓ Counselling Request & Teacher Review flow passed")

    # ─────────────────────────────────────────
    # MODULE 5: TESTS & PAPERS
    # ─────────────────────────────────────────
    print("\n[Module 5] Mock Tests & Question Papers Tests:")

    # 1. Question papers
    papers = list_papers(exam=None, subject=None, year=None, topic=None, skip=0, limit=30, db=db, current_user=student)
    assert papers["total"] >= 3
    print(f"  ✓ Question Papers Library: {papers['total']} papers available")

    # 2. Tests list & test attempt flow
    tests = list_tests(subject=None, skip=0, limit=30, db=db, current_user=student)
    assert tests["total"] >= 2
    test_id = tests["items"][0]["id"]

    start_res = start_test_attempt(test_id=test_id, db=db, current_user=student)
    attempt_id = start_res["attempt_id"]

    test_detail = get_test(test_id=test_id, db=db, current_user=student)
    questions = test_detail["questions"]
    assert len(questions) > 0

    answers_payload = [
        {"question_id": q["id"], "student_answer": "1" if q["question_type"] == "mcq" else "True"}
        for q in questions[:3]
    ]
    submit_res = submit_test_attempt(
        test_id=test_id,
        payload={"attempt_id": attempt_id, "time_taken_seconds": 180, "answers": answers_payload},
        db=db,
        current_user=student
    )
    assert "accuracy" in submit_res
    assert "topic_breakdown" in submit_res
    assert submit_res["skill_profile_updated"] is True
    print(f"  ✓ Test Attempt Submitted & Scored (Accuracy: {submit_res['accuracy']}%, SkillProfile updated: {submit_res['skill_profile_updated']})")

    res_detail = get_attempt_result(attempt_id=attempt_id, db=db, current_user=student)
    assert "answers_detail" in res_detail
    print(f"  ✓ Detailed Test Analytics & Breakdown retrieved")

    adapt_res = generate_adaptive_test(payload={"subject": "Biology", "num_questions": 5}, db=db, current_user=student)
    assert adapt_res["adaptive"] is True
    print(f"  ✓ Adaptive Practice Generator: created test targeting {adapt_res['weak_topics_targeted']}")

    # ─────────────────────────────────────────
    # MODULE 6: AI CHATBOT (RAG)
    # ─────────────────────────────────────────
    print("\n[Module 6] AI Chatbot (StudyMatch Assistant) Tests:")

    docs = list_documents(doc_type=None, skip=0, limit=30, db=db, current_user=student)
    assert docs["total"] >= 3
    print(f"  ✓ Verified Guidance Knowledge Base: {docs['total']} documents")

    sess_res = create_session(payload={"title": "Career Query Session"}, db=db, current_user=student)
    session_id = sess_res["session_id"]

    msg_res = send_message(
        session_id=session_id,
        payload={"message": "What is the eligibility for JEE Main and what are top colleges?"},
        db=db,
        current_user=student
    )
    assert "bot_response" in msg_res
    assert len(msg_res["bot_response"]) > 20
    assert "⚠️ *Important:*" in msg_res["bot_response"]
    print(f"  ✓ RAG Chatbot Response generated (Length: {len(msg_res['bot_response'])} chars, Disclaimer verified)")
    if msg_res.get("sources"):
        print(f"    Sources cited: {[s['title'] for s in msg_res['sources']]}")

    hist = get_messages(session_id=session_id, skip=0, limit=50, db=db, current_user=student)
    assert len(hist) >= 2
    print(f"  ✓ Chat history preserved: {len(hist)} messages in session")

    db.close()
    print("\n=======================================================")
    print("🎉 ALL PHASE 1 INTEGRATION TESTS PASSED! 🎉")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
