"""Locks in the exact seed-data counts after the full migration chain
(including 0025's repair/re-seed) runs once on a normal database --
guards against the repair migration ever duplicating rows that are
already present, which the ON CONFLICT DO NOTHING clauses are meant
to prevent."""


def test_full_reference_data_present_and_not_duplicated(client):
    careers = client.get("/careers").json()
    assert len(careers) == 16

    categories = client.get("/careers/categories").json()
    assert len(categories) == 12

    languages = client.get("/languages").json()
    assert len(languages) == 5

    courses = client.get("/courses").json()
    assert len(courses) == 15
