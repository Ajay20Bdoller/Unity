"""Uses the seeded "intro-to-programming" course (2 modules, 3 lessons)
that migration 0006 creates — real seed data, not fixture-created.
"""


def _get_seeded_course(client):
    res = client.get("/courses")
    assert res.status_code == 200
    courses = res.json()
    course = next(c for c in courses if c["slug"] == "intro-to-programming")
    return course


def _get_lesson_ids_in_order(client):
    detail = client.get("/courses/intro-to-programming").json()
    return [lesson["id"] for module in detail["modules"] for lesson in module["lessons"]]


def test_course_listing_is_public(client):
    courses = client.get("/courses")
    assert courses.status_code == 200
    assert any(c["slug"] == "intro-to-programming" for c in courses.json())


def test_course_detail_requires_login(client):
    res = client.get("/courses/intro-to-programming")
    assert res.status_code == 401


def test_course_detail_for_logged_in_user(student_client):
    detail = student_client.get("/courses/intro-to-programming")
    assert detail.status_code == 200
    assert len(detail.json()["modules"]) == 2


def test_completing_a_lesson_before_enrolling_is_rejected(student_client):
    lesson_ids = _get_lesson_ids_in_order(student_client)
    res = student_client.post(f"/students/me/lessons/{lesson_ids[0]}/complete")
    assert res.status_code == 400


def test_enroll_progress_and_continue_learning(student_client):
    course = _get_seeded_course(student_client)
    lesson_ids = _get_lesson_ids_in_order(student_client)
    assert len(lesson_ids) == 3

    enroll = student_client.post(f"/students/me/enrollments/{course['id']}")
    assert enroll.status_code == 204

    # idempotent — enrolling again doesn't error or duplicate
    again = student_client.post(f"/students/me/enrollments/{course['id']}")
    assert again.status_code == 204

    enrollments = student_client.get("/students/me/enrollments").json()
    mine = next(e for e in enrollments if e["course"]["slug"] == "intro-to-programming")
    assert mine["progress_percent"] == 0
    assert mine["completed_lessons"] == 0
    assert mine["total_lessons"] == 3

    complete = student_client.post(f"/students/me/lessons/{lesson_ids[0]}/complete")
    assert complete.status_code == 204

    enrollments = student_client.get("/students/me/enrollments").json()
    mine = next(e for e in enrollments if e["course"]["slug"] == "intro-to-programming")
    assert mine["completed_lessons"] == 1
    assert mine["progress_percent"] == 33  # round(1/3 * 100)

    continue_learning = student_client.get("/students/me/continue-learning").json()
    entry = next(c for c in continue_learning if c["course"]["slug"] == "intro-to-programming")
    assert entry["next_lesson"]["id"] == lesson_ids[1]  # first *incomplete* lesson
    assert entry["progress_percent"] == 33

    progress_view = student_client.get("/students/me/courses/intro-to-programming").json()
    assert progress_view["enrolled"] is True
    flags = [
        lesson["completed"] for module in progress_view["modules"] for lesson in module["lessons"]
    ]
    assert flags == [True, False, False]


def test_non_admin_cannot_create_courses(student_client):
    res = student_client.post(
        "/admin/courses",
        json={"slug": "x", "title": "X", "description": "y"},
    )
    assert res.status_code == 403
