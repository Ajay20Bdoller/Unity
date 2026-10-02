def test_photo_url_saves_and_appears_on_own_profile(mentor_client):
    update = mentor_client.patch("/mentors/me", json={"photo_url": "https://example.com/me.jpg"})
    assert update.status_code == 200
    assert update.json()["photo_url"] == "https://example.com/me.jpg"

    own = mentor_client.get("/mentors/me").json()
    assert own["photo_url"] == "https://example.com/me.jpg"


def test_photo_url_appears_on_public_listing_once_approved(mentor_client, admin_client):
    mentor_client.patch("/mentors/me", json={"photo_url": "https://example.com/approved.jpg"})
    admin_list = admin_client.get("/admin/mentors").json()
    mentor_id = next(m for m in admin_list if m["full_name"] == "Role Matrix Mentor")["user_id"]
    admin_client.post(f"/admin/mentors/{mentor_id}/approve")

    public = admin_client.get("/mentors").json()
    mine = next(m for m in public if m["user_id"] == mentor_id)
    assert mine["photo_url"] == "https://example.com/approved.jpg"


def test_expertise_can_be_added_then_removed(mentor_client):
    categories = mentor_client.get("/careers/categories").json()
    category_id = categories[0]["id"]

    add = mentor_client.post(f"/mentors/me/expertise/{category_id}")
    assert add.status_code == 204
    assert categories[0]["key"] in mentor_client.get("/mentors/me").json()["expertise"]

    remove = mentor_client.delete(f"/mentors/me/expertise/{category_id}")
    assert remove.status_code == 204
    assert categories[0]["key"] not in mentor_client.get("/mentors/me").json()["expertise"]

    # removing again (already gone) doesn't error
    remove_again = mentor_client.delete(f"/mentors/me/expertise/{category_id}")
    assert remove_again.status_code == 204


def test_language_can_be_added_then_removed(mentor_client):
    languages = mentor_client.get("/languages").json()
    code = languages[0]["code"]

    add = mentor_client.post(f"/mentors/me/languages/{code}")
    assert add.status_code == 204
    assert code in mentor_client.get("/mentors/me").json()["languages"]

    remove = mentor_client.delete(f"/mentors/me/languages/{code}")
    assert remove.status_code == 204
    assert code not in mentor_client.get("/mentors/me").json()["languages"]


def test_expertise_and_language_removal_requires_mentor_role(student_client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    assert student_client.delete(f"/mentors/me/expertise/{fake_id}").status_code == 403
    assert student_client.delete("/mentors/me/languages/en").status_code == 403
