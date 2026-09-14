def test_admin_course_detail_works_for_draft_course(admin_client, student_client):
    course = admin_client.post(
        "/admin/courses",
        json={"slug": "draft-test-course", "title": "Draft Test", "description": "d"},
    ).json()
    assert course["published"] is False

    regular_attempt = student_client.get("/courses/draft-test-course")
    assert regular_attempt.status_code == 404

    admin_detail = admin_client.get(f"/admin/courses/{course['id']}")
    assert admin_detail.status_code == 200
    assert admin_detail.json()["modules"] == []


def test_add_module_and_external_resource_lesson(admin_client):
    course = admin_client.post(
        "/admin/courses",
        json={"slug": "content-test-course", "title": "Content Test", "description": "d"},
    ).json()

    module = admin_client.post(
        f"/admin/courses/{course['id']}/modules",
        json={"title": "Getting Started", "display_order": 0},
    )
    assert module.status_code == 201
    module_id = module.json()["id"]

    lesson = admin_client.post(
        f"/admin/courses/modules/{module_id}/lessons",
        json={
            "title": "Setup guide",
            "content_type": "external_resource",
            "content_url": "https://example.com/setup",
            "display_order": 0,
        },
    )
    assert lesson.status_code == 201
    assert lesson.json()["content_type"] == "external_resource"
    assert lesson.json()["content_url"] == "https://example.com/setup"

    detail = admin_client.get(f"/admin/courses/{course['id']}").json()
    assert len(detail["modules"]) == 1
    assert len(detail["modules"][0]["lessons"]) == 1
    assert detail["modules"][0]["lessons"][0]["title"] == "Setup guide"


def test_non_admin_blocked_from_course_content_management(student_client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    assert student_client.get(f"/admin/courses/{fake_id}").status_code == 403
    assert (
        student_client.post(f"/admin/courses/{fake_id}/modules", json={"title": "x"}).status_code
        == 403
    )
