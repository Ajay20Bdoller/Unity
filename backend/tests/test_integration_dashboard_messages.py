def test_seeded_messages_are_visible_to_any_logged_in_user(student_client):
    res = student_client.get("/dashboard-messages")
    assert res.status_code == 200
    messages = res.json()
    assert len(messages) == 2  # seeded in migration 0022
    assert all(m["active"] for m in messages)


def test_logged_out_blocked(client):
    assert client.get("/dashboard-messages").status_code == 401


def test_non_admin_blocked_from_managing_messages(student_client):
    assert student_client.get("/admin/dashboard-messages").status_code == 403
    assert (
        student_client.post("/admin/dashboard-messages", json={"message": "x"}).status_code == 403
    )


def test_admin_can_create_edit_delete_and_deactivate(admin_client, student_client):
    create = admin_client.post(
        "/admin/dashboard-messages",
        json={"message": "Keep going.", "attribution": "Someone wise", "display_order": 5},
    )
    assert create.status_code == 201
    message_id = create.json()["id"]

    visible = student_client.get("/dashboard-messages").json()
    assert any(m["message"] == "Keep going." for m in visible)

    update = admin_client.patch(
        f"/admin/dashboard-messages/{message_id}", json={"active": False}
    )
    assert update.status_code == 200
    assert update.json()["active"] is False

    still_visible = student_client.get("/dashboard-messages").json()
    assert not any(m["message"] == "Keep going." for m in still_visible)

    delete = admin_client.delete(f"/admin/dashboard-messages/{message_id}")
    assert delete.status_code == 204

    admin_list = admin_client.get("/admin/dashboard-messages").json()
    assert not any(m["id"] == message_id for m in admin_list)
