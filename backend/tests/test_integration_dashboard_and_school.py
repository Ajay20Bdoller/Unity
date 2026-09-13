def test_default_dashboard_sections_resolve_in_order_for_student(student_client):
    sections = student_client.get("/dashboard/sections").json()
    keys = [s["key"] for s in sections]
    assert keys == ["welcome", "ai_assistant", "continue_learning", "recent_announcements"]


def test_admin_disabling_a_section_hides_it_for_that_role(admin_client, student_client):
    all_sections = admin_client.get("/admin/dashboard-sections").json()
    ai_section = next(s for s in all_sections if s["key"] == "ai_assistant")

    disable = admin_client.put(
        f"/admin/dashboard-sections/{ai_section['id']}/roles/student",
        json={"enabled": False, "display_order": 1},
    )
    assert disable.status_code == 200

    sections = student_client.get("/dashboard/sections").json()
    assert "ai_assistant" not in [s["key"] for s in sections]


def test_non_admin_cannot_modify_dashboard_sections(student_client):
    res = student_client.get("/admin/dashboard-sections")
    assert res.status_code == 403


def test_school_admin_sees_only_matching_students(school_admin_client):
    from fastapi.testclient import TestClient

    from app.main import app

    # school_admin_client (conftest.py) registers with school_name="School"
    matching = TestClient(app)
    matching.post(
        "/auth/register",
        json={
            "full_name": "Matching Student",
            "role": "student",
            "mobile_number": "9500000001",
            "password": "TestPass123!",
            "date_of_birth": "2010-01-01",
            "school_name": "School",
            "parent_name": "Parent",
            "parent_relation": "Mother",
            "address": "addr",
            "district": "d",
            "state": "Delhi",
        },
    )
    non_matching = TestClient(app)
    non_matching.post(
        "/auth/register",
        json={
            "full_name": "Non-matching Student",
            "role": "student",
            "mobile_number": "9500000002",
            "password": "TestPass123!",
            "date_of_birth": "2010-01-01",
            "school_name": "A Totally Different School",
            "parent_name": "Parent",
            "parent_relation": "Mother",
            "address": "addr",
            "district": "d",
            "state": "Delhi",
        },
    )

    students = school_admin_client.get("/schools/me/students").json()
    names = [s["full_name"] for s in students]
    assert "Matching Student" in names
    assert "Non-matching Student" not in names


def test_non_school_admin_blocked(student_client):
    res = student_client.get("/schools/me/students")
    assert res.status_code == 403
