import uuid

import pytest
from pydantic import ValidationError

from app.schemas.assessment import AssessmentSubmission


def test_submission_rejects_empty_responses():
    with pytest.raises(ValidationError):
        AssessmentSubmission(responses=[])


def test_submission_accepts_responses():
    sub = AssessmentSubmission(
        responses=[{"question_id": uuid.uuid4(), "selected_option_value": "a"}]
    )
    assert len(sub.responses) == 1
