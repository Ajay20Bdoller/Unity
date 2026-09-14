"""Uses the real seeded career data from migration 0005: 12 categories,
4 careers (incl. software-engineer with a Hindi translation and a
related-career link to data-scientist).
"""


def test_categories_and_listing_are_public(client):
    categories = client.get("/careers/categories")
    assert categories.status_code == 200
    assert len(categories.json()) == 12

    careers = client.get("/careers")
    assert careers.status_code == 200
    assert any(c["slug"] == "software-engineer" for c in careers.json())


def test_category_filter_and_search(client):
    filtered = client.get("/careers?category=medicine").json()
    assert all(c["category_key"] == "medicine" for c in filtered)
    assert any(c["slug"] == "doctor" for c in filtered)

    searched = client.get("/careers?q=data").json()
    assert any(c["slug"] == "data-scientist" for c in searched)
    assert all("data" in c["title"].lower() for c in searched)


def test_detail_requires_login(client):
    res = client.get("/careers/software-engineer")
    assert res.status_code == 401


def test_detail_includes_related_careers_and_category(student_client):
    detail = student_client.get("/careers/software-engineer")
    assert detail.status_code == 200
    body = detail.json()
    assert body["category"]["key"] == "technology_ai"
    assert any(r["slug"] == "data-scientist" for r in body["related_careers"])
    assert body["language"] == "en"


def test_translation_resolves_and_missing_language_falls_back_to_english(student_client):
    hindi = student_client.get("/careers/software-engineer?lang=hi").json()
    assert hindi["language"] == "hi"
    assert hindi["title"] != "Software Engineer"  # actually translated

    bengali = student_client.get("/careers/software-engineer?lang=bn").json()
    assert bengali["language"] == "en"  # no bn translation seeded -> falls back
    assert bengali["title"] == "Software Engineer"


def test_unknown_slug_is_404(student_client):
    res = student_client.get("/careers/not-a-real-career")
    assert res.status_code == 404


def test_student_interest_toggle_is_idempotent(student_client):
    career = student_client.get("/careers/software-engineer").json()
    career_id = career["id"]

    add = student_client.post(f"/students/me/career-interests/{career_id}")
    assert add.status_code == 204
    add_again = student_client.post(f"/students/me/career-interests/{career_id}")
    assert add_again.status_code == 204  # not a 409 -- idempotent by design

    mine = student_client.get("/students/me/career-interests").json()
    assert len(mine) == 1
    assert mine[0]["slug"] == "software-engineer"

    remove = student_client.delete(f"/students/me/career-interests/{career_id}")
    assert remove.status_code == 204
    assert student_client.get("/students/me/career-interests").json() == []


def test_non_admin_blocked_from_admin_career_endpoints(student_client):
    res = student_client.post(
        "/admin/careers/categories", json={"key": "new_cat", "name": "New"}
    )
    assert res.status_code == 403


def test_admin_can_create_category_and_career(admin_client):
    category = admin_client.post(
        "/admin/careers/categories", json={"key": "integration_test_cat", "name": "Test Cat"}
    )
    assert category.status_code == 201
    category_id = category.json()["id"]

    duplicate = admin_client.post(
        "/admin/careers/categories", json={"key": "integration_test_cat", "name": "Test Cat 2"}
    )
    assert duplicate.status_code == 409

    career = admin_client.post(
        "/admin/careers",
        json={
            "category_id": category_id,
            "slug": "integration-test-career",
            "title": "Integration Test Career",
            "description": "A career created by a test.",
        },
    )
    assert career.status_code == 201

    listed = admin_client.get("/careers").json()
    assert any(c["slug"] == "integration-test-career" for c in listed)
