def test_draft_never_visible_to_anyone(admin_client, student_client):
    draft = admin_client.post(
        "/admin/announcements",
        json={"title": "Draft only", "content": "secret", "language_code": "en"},
    )
    assert draft.status_code == 201
    assert draft.json()["publish_status"] == "draft"

    visible = student_client.get("/announcements").json()
    assert not any(a["title"] == "Draft only" for a in visible)


def test_audience_filtering(admin_client, student_client, parent_client):
    student_only = admin_client.post(
        "/admin/announcements",
        json={
            "title": "Student only announcement",
            "content": "Scholarship deadline",
            "audience": ["student"],
        },
    ).json()
    admin_client.post(f"/admin/announcements/{student_only['id']}/publish")

    everyone = admin_client.post(
        "/admin/announcements",
        json={"title": "Everyone announcement", "content": "Platform update"},
    ).json()
    admin_client.post(f"/admin/announcements/{everyone['id']}/publish")

    student_feed = [a["title"] for a in student_client.get("/announcements").json()]
    assert "Student only announcement" in student_feed
    assert "Everyone announcement" in student_feed

    parent_feed = [a["title"] for a in parent_client.get("/announcements").json()]
    assert "Student only announcement" not in parent_feed
    assert "Everyone announcement" in parent_feed


def test_non_admin_cannot_publish(student_client):
    res = student_client.post("/admin/announcements", json={"title": "x", "content": "y"})
    assert res.status_code == 403


def test_admin_listing_includes_drafts(admin_client):
    admin_client.post("/admin/announcements", json={"title": "Another draft", "content": "y"})
    all_including_drafts = admin_client.get("/admin/announcements").json()
    assert any(a["title"] == "Another draft" for a in all_including_drafts)
