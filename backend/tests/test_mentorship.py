import pytest
from pydantic import ValidationError

from app.schemas.mentorship import MentorshipFeedbackCreate


def test_feedback_rating_bounds():
    MentorshipFeedbackCreate(rating=1)
    MentorshipFeedbackCreate(rating=5)
    with pytest.raises(ValidationError):
        MentorshipFeedbackCreate(rating=0)
    with pytest.raises(ValidationError):
        MentorshipFeedbackCreate(rating=6)
