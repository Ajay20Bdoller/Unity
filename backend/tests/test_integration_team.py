def test_public_team_listing_starts_empty(client):
    res = client.get("/about-us/team")
    assert res.status_code == 200
    assert res.json() == []


def test_non_admin_blocked_from_team_management(student_client):
    res = student_client.post(
        "/admin/team", json={"full_name": "x", "role_title": "y"}
    )
    assert res.status_code == 403
    assert student_client.get("/admin/team").status_code == 403


def test_admin_can_create_edit_and_delete_a_profile(admin_client, client):
    create = admin_client.post(
        "/admin/team",
        json={
            "full_name": "Founder Name",
            "role_title": "Founder & CTO",
            "bio": "Building Unity.",
            "display_order": 0,
        },
    )
    assert create.status_code == 201
    member_id = create.json()["id"]

    public = client.get("/about-us/team").json()
    assert len(public) == 1
    assert public[0]["full_name"] == "Founder Name"
    assert public[0]["role_title"] == "Founder & CTO"

    update = admin_client.patch(f"/admin/team/{member_id}", json={"bio": "Updated bio."})
    assert update.status_code == 200
    assert update.json()["bio"] == "Updated bio."

    delete = admin_client.delete(f"/admin/team/{member_id}")
    assert delete.status_code == 204
    assert client.get("/about-us/team").json() == []


def test_team_ordered_by_display_order(admin_client, client):
    admin_client.post(
        "/admin/team", json={"full_name": "Second", "role_title": "Co-founder", "display_order": 1}
    )
    admin_client.post(
        "/admin/team", json={"full_name": "First", "role_title": "Founder", "display_order": 0}
    )

    listing = client.get("/about-us/team").json()
    assert [m["full_name"] for m in listing] == ["First", "Second"]
