import uuid

from app.schemas.career import CareerCreate, CareerListItem


def test_career_create_schema_accepts_minimal_payload():
    payload = CareerCreate(
        category_id=uuid.uuid4(),
        slug="test-career",
        title="Test Career",
        description="A description.",
    )
    assert payload.subjects is None
    assert payload.slug == "test-career"


def test_career_list_item_round_trips():
    item = CareerListItem(
        id=uuid.uuid4(),
        slug="software-engineer",
        title="Software Engineer",
        description="Builds software.",
        category_key="technology_ai",
    )
    assert item.category_key == "technology_ai"
