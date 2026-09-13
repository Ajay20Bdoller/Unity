def test_new_mentor_is_pending_and_hidden_from_public_list(mentor_client, admin_client):
    public_list = admin_client.get("/mentors").json()  # public endpoint, any client works
    assert not any(m["full_name"] == "Role Matrix Mentor" for m in public_list)

    admin_list = admin_client.get("/admin/mentors").json()
    mine = next(m for m in admin_list if m["full_name"] == "Role Matrix Mentor")
    assert mine["is_approved"] is False


def test_one_click_approve_makes_mentor_visible(mentor_client, admin_client):
    admin_list = admin_client.get("/admin/mentors").json()
    mentor_id = next(m for m in admin_list if m["full_name"] == "Role Matrix Mentor")["user_id"]

    approve = admin_client.post(f"/admin/mentors/{mentor_id}/approve")
    assert approve.status_code == 200
    assert approve.json()["is_approved"] is True

    public_list = admin_client.get("/mentors").json()
    assert any(m["user_id"] == mentor_id for m in public_list)


def test_unapprove_hides_mentor_again(mentor_client, admin_client):
    admin_list = admin_client.get("/admin/mentors").json()
    mentor_id = next(m for m in admin_list if m["full_name"] == "Role Matrix Mentor")["user_id"]
    admin_client.post(f"/admin/mentors/{mentor_id}/approve")

    unapprove = admin_client.post(f"/admin/mentors/{mentor_id}/unapprove")
    assert unapprove.status_code == 200
    assert unapprove.json()["is_approved"] is False

    public_list = admin_client.get("/mentors").json()
    assert not any(m["user_id"] == mentor_id for m in public_list)


def test_non_admin_blocked_from_mentor_approval(student_client, mentor_client):
    admin_list = student_client.get("/admin/mentors")
    assert admin_list.status_code == 403

    approve = student_client.post(
        "/admin/mentors/00000000-0000-0000-0000-000000000000/approve"
    )
    assert approve.status_code == 403
