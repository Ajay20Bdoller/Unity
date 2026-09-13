from app.schemas.announcement import AnnouncementCreate


def test_announcement_defaults_to_english_and_no_audience_restriction():
    payload = AnnouncementCreate(title="Hi", content="Body")
    assert payload.language_code == "en"
    assert payload.audience is None
