"""Uses the seeded "Explore Your Career Interests" assessment (10
questions) that migration 0008 creates.
"""


def _get_seeded_assessment(client):
    res = client.get("/assessments")
    assert res.status_code == 200
    return res.json()[0]


def test_questions_never_leak_weights(client):
    assessment = _get_seeded_assessment(client)
    questions = client.get(f"/assessments/{assessment['id']}/questions").json()
    assert len(questions) == 10
    for q in questions:
        for option in q["options"]:
            assert set(option.keys()) == {"value", "label"}


def test_partial_submission_rejected(student_client):
    assessment = _get_seeded_assessment(student_client)
    questions = student_client.get(f"/assessments/{assessment['id']}/questions").json()

    responses = [{"question_id": questions[0]["id"], "selected_option_value": "a"}]
    res = student_client.post(
        f"/students/me/assessments/{assessment['id']}/submit", json={"responses": responses}
    )
    assert res.status_code == 400


def test_full_submission_scores_and_persists_result(student_client):
    assessment = _get_seeded_assessment(student_client)
    questions = student_client.get(f"/assessments/{assessment['id']}/questions").json()

    responses = [{"question_id": q["id"], "selected_option_value": "a"} for q in questions]
    submit = student_client.post(
        f"/students/me/assessments/{assessment['id']}/submit", json={"responses": responses}
    )
    assert submit.status_code == 200
    body = submit.json()
    assert len(body["suggested_categories"]) > 0
    assert len(body["suggested_categories"]) <= 3
    assert "exploratory" in body["note"].lower()

    results = student_client.get(f"/students/me/assessments/{assessment['id']}/results").json()
    assert len(results) == 1
    assert results[0]["id"] == body["id"]


def test_invalid_option_value_rejected(student_client):
    assessment = _get_seeded_assessment(student_client)
    questions = student_client.get(f"/assessments/{assessment['id']}/questions").json()
    responses = [
        {"question_id": q["id"], "selected_option_value": "not-a-real-option"} for q in questions
    ]
    res = student_client.post(
        f"/students/me/assessments/{assessment['id']}/submit", json={"responses": responses}
    )
    assert res.status_code == 400
