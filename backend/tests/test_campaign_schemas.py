from app.models.campaign import CampaignType
from app.schemas.campaign import CampaignCreate


def test_campaign_create_accepts_all_types():
    for campaign_type in CampaignType:
        payload = CampaignCreate(key="k", name="N", campaign_type=campaign_type)
        assert payload.campaign_type == campaign_type
        assert payload.active is True
