"""Doc-21's role security matrix, automated: try every role against
every other role's protected endpoints and confirm they're rejected.
Uses the pre-authenticated *_client fixtures from conftest.py.
"""


def test_student_only_endpoint_blocks_everyone_else(
    parent_client, mentor_client, school_admin_client, admin_client
):
    for other in [parent_client, mentor_client, school_admin_client, admin_client]:
        res = other.get("/students/me")
        assert res.status_code == 403, res.text


def test_parent_only_endpoint_blocks_everyone_else(
    student_client, mentor_client, school_admin_client, admin_client
):
    for other in [student_client, mentor_client, school_admin_client, admin_client]:
        res = other.get("/parents/me/guardians")
        assert res.status_code == 403, res.text


def test_mentor_only_endpoint_blocks_everyone_else(
    student_client, parent_client, school_admin_client, admin_client
):
    for other in [student_client, parent_client, school_admin_client, admin_client]:
        res = other.get("/mentors/me/requests")
        assert res.status_code == 403, res.text


def test_school_admin_only_endpoint_blocks_everyone_else(
    student_client, parent_client, mentor_client, admin_client
):
    for other in [student_client, parent_client, mentor_client, admin_client]:
        res = other.get("/schools/me/students")
        assert res.status_code == 403, res.text


def test_admin_only_endpoint_blocks_everyone_else(
    student_client, parent_client, mentor_client, school_admin_client
):
    for other in [student_client, parent_client, mentor_client, school_admin_client]:
        res = other.get("/admin/users")
        assert res.status_code == 403, res.text


def test_unauthenticated_request_blocked_on_every_role_endpoint(client):
    for path in [
        "/students/me",
        "/parents/me/guardians",
        "/mentors/me/requests",
        "/schools/me/students",
        "/admin/users",
    ]:
        res = client.get(path)
        assert res.status_code == 401, f"{path}: {res.text}"


def test_admin_can_access_its_own_endpoint(admin_client):
    res = admin_client.get("/admin/users")
    assert res.status_code == 200
    assert any(u["email"] == "rolematrix-admin@example.com" for u in res.json())
