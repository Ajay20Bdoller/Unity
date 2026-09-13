def test_registration_with_valid_campaign_key_is_attributed(admin_client):
    campaign = admin_client.post(
        "/admin/campaigns",
        json={"key": "integration-campaign", "name": "Integration Campaign", "campaign_type": "school"},
    )
    assert campaign.status_code == 201
    campaign_id = campaign.json()["id"]

    duplicate_key = admin_client.post(
        "/admin/campaigns",
        json={"key": "integration-campaign", "name": "Dup", "campaign_type": "school"},
    )
    assert duplicate_key.status_code == 409

    from fastapi.testclient import TestClient

    from app.main import app

    registrant = TestClient(app)
    reg = registrant.post(
        "/auth/register",
        json={
            "full_name": "Campaign Student",
            "role": "student",
            "mobile_number": "9400000001",
            "password": "TestPass123!",
            "date_of_birth": "2010-01-01",
            "school_name": "School",
            "parent_name": "Parent",
            "parent_relation": "Mother",
            "address": "addr",
            "district": "d",
            "state": "Delhi",
            "campaign_key": "integration-campaign",
            "source": "flyer",
        },
    )
    assert reg.status_code == 201

    registrations = admin_client.get(f"/admin/campaigns/{campaign_id}/registrations").json()
    assert len(registrations) == 1
    assert registrations[0]["source"] == "flyer"


def test_registration_with_unknown_campaign_key_still_succeeds(client):
    res = client.post(
        "/auth/register",
        json={
            "full_name": "No Campaign Student",
            "role": "student",
            "mobile_number": "9400000002",
            "password": "TestPass123!",
            "date_of_birth": "2010-01-01",
            "school_name": "School",
            "parent_name": "Parent",
            "parent_relation": "Mother",
            "address": "addr",
            "district": "d",
            "state": "Delhi",
            "campaign_key": "this-campaign-does-not-exist",
        },
    )
    assert res.status_code == 201


def test_non_admin_blocked_from_campaigns(student_client):
    res = student_client.get("/admin/campaigns")
    assert res.status_code == 403


def test_campaign_toggle_active(admin_client):
    campaign = admin_client.post(
        "/admin/campaigns",
        json={"key": "toggle-campaign", "name": "Toggle", "campaign_type": "online"},
    ).json()

    update = admin_client.patch(f"/admin/campaigns/{campaign['id']}", json={"active": False})
    assert update.status_code == 200
    assert update.json()["active"] is False
