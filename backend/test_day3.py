"""
Unit & Integration Test Suite for Day 3: Intelligent Study Groups & Schedules
Tests Optimization Matching Algorithm, 3-5 member constraint, Peer-Teaching pairs,
Schedule Matching, and PostgreSQL persistence.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Student, StudyGroup, GroupMember, TeachingPair, StudySchedule
from ml.group_matcher import (
    form_balanced_study_groups,
    generate_peer_teaching_recommendations,
    match_study_schedules,
)
from routers import groups as groups_router


def run_day3_tests():
    db = SessionLocal()
    print("--- Starting Day 3 Intelligent Study Groups & Schedules Tests ---")

    try:
        # 1. Test Group Matching Algorithm Constraints
        print("[Optimization Group Matcher Unit Test]")
        mock_students = [
            {"id": 1, "name": "Student A", "weak_topics": ["SQL"], "strong_topics": ["Calculus"], "mastery_scores": {"SQL": 30, "Calculus": 95}},
            {"id": 2, "name": "Student B", "weak_topics": ["Calculus"], "strong_topics": ["SQL"], "mastery_scores": {"Calculus": 40, "SQL": 90}},
            {"id": 3, "name": "Student C", "weak_topics": ["OOP"], "strong_topics": ["SQL"], "mastery_scores": {"OOP": 35, "SQL": 85}},
            {"id": 4, "name": "Student D", "weak_topics": ["SQL"], "strong_topics": ["OOP"], "mastery_scores": {"SQL": 45, "OOP": 92}},
            {"id": 5, "name": "Student E", "weak_topics": ["Mitosis"], "strong_topics": ["DNA"], "mastery_scores": {"Mitosis": 25, "DNA": 88}},
            {"id": 6, "name": "Student F", "weak_topics": ["DNA"], "strong_topics": ["Mitosis"], "mastery_scores": {"DNA": 30, "Mitosis": 90}},
            {"id": 7, "name": "Student G", "weak_topics": ["DNA"], "strong_topics": ["Mitosis"], "mastery_scores": {"DNA": 40, "Mitosis": 85}},
            {"id": 8, "name": "Student H", "weak_topics": ["Calculus"], "strong_topics": ["OOP"], "mastery_scores": {"Calculus": 35, "OOP": 90}},
        ]

        test_groups = form_balanced_study_groups(mock_students, min_size=3, max_size=5)
        assert len(test_groups) == 2, f"Expected 2 groups for 8 students, got {len(test_groups)}"
        for g in test_groups:
            size = g["member_count"]
            assert 3 <= size <= 5, f"Group size {size} violates constraint [3, 5]!"
            assert g["coverage_metrics"]["coverage_rate"] > 0
            print(f"  ✓ {g['group_name']}: {size} members, Coverage: {g['coverage_metrics']['coverage_rate']}%")

        # 2. Test Peer-Teaching Generation
        print("\n[Peer Teaching Recommendations]")
        sample_members = test_groups[0]["members"]
        teaching_pairs = generate_peer_teaching_recommendations(sample_members)
        assert len(teaching_pairs) >= 1
        for p in teaching_pairs:
            assert "demonstrated strong mastery in" in p["reason"]
            assert p["tutor_id"] != p["learner_id"]
        print(f"  ✓ Generated {len(teaching_pairs)} peer-teaching pairings with pedagogical justification reasons.")
        print(f"    Sample: {teaching_pairs[0]['tutor_name']} tutors {teaching_pairs[0]['learner_name']} in '{teaching_pairs[0]['topic_name']}'")

        # 3. Test Schedule Matching
        print("\n[Schedule Overlap Matcher]")
        mock_schedules = {
            1: [{"day_of_week": "Monday", "start_time": "17:00", "end_time": "19:00"}],
            2: [{"day_of_week": "Monday", "start_time": "17:00", "end_time": "19:00"}, {"day_of_week": "Wednesday", "start_time": "18:00", "end_time": "20:00"}],
            3: [{"day_of_week": "Monday", "start_time": "17:00", "end_time": "19:00"}],
            4: [{"day_of_week": "Tuesday", "start_time": "16:00", "end_time": "18:00"}],
        }
        names = {1: "A", 2: "B", 3: "C", 4: "D"}
        common_slots = match_study_schedules(mock_schedules, names)
        assert len(common_slots) >= 1
        top_slot = common_slots[0]
        assert top_slot["day_of_week"] == "Monday"
        assert top_slot["available_count"] == 3
        print(f"  ✓ Top common study session: {top_slot['day_of_week']} {top_slot['start_time']}-{top_slot['end_time']} ({top_slot['available_count']}/{top_slot['total_members']} members available)")

        # 4. Test Student Schedule CRUD API
        print("\n[Student Schedule Management Endpoints]")
        student = db.query(Student).filter(Student.role == "student").first()
        assert student is not None

        new_slot_req = groups_router.ScheduleSlotCreate(
            day_of_week="Saturday",
            start_time="14:00",
            end_time="16:00"
        )
        saved_slot = groups_router.add_study_schedule_slot(new_slot_req, current_user=student, db=db)
        assert saved_slot.id is not None
        assert saved_slot.day_of_week == "Saturday"
        print(f"  ✓ Student added schedule slot: {saved_slot.day_of_week} {saved_slot.start_time}-{saved_slot.end_time}")

        my_slots = groups_router.get_my_study_schedules(current_user=student, db=db)
        assert any(s.day_of_week == "Saturday" for s in my_slots)
        print(f"  ✓ Retrieved {len(my_slots)} active schedule slots for student '{student.name}'.")

        # 5. Test Teacher Generate Groups API (DB Persistence)
        print("\n[Teacher Group Generation & Persistence]")
        teacher = db.query(Student).filter(Student.role == "teacher").first()
        assert teacher is not None

        gen_req = groups_router.GenerateGroupsRequest(min_size=3, max_size=5, reset_existing=True)
        persisted_groups = groups_router.generate_study_groups(req=gen_req, current_user=teacher, db=db)
        assert len(persisted_groups) >= 2, f"Expected at least 2 groups from database, got {len(persisted_groups)}"
        for pg in persisted_groups:
            assert 3 <= pg.member_count <= 5, f"Persisted group {pg.name} size {pg.member_count} not in [3, 5]"
            assert len(pg.teaching_pairs) >= 1
            print(f"  ✓ Persisted {pg.name}: {pg.member_count} members | Coverage: {pg.coverage_rate}% | {len(pg.teaching_pairs)} Teaching Pairs | {len(pg.common_schedules)} Schedule Matches")

        # 6. Test Student View My Group
        print("\n[Student Group View]")
        my_group = groups_router.get_my_study_group(current_user=student, db=db)
        assert my_group is not None
        assert any(m.student_id == student.id for m in my_group.members)
        print(f"  ✓ Student '{student.name}' retrieved assigned group '{my_group.name}' with {my_group.member_count} members.")

        print("\n=======================================================")
        print("🎉 ALL DAY 3 STUDY GROUPS & SCHEDULES TESTS PASSED! 🎉")
        print("=======================================================\n")

    finally:
        db.close()


if __name__ == "__main__":
    run_day3_tests()
