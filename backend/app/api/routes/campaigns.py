import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.campaign import Campaign, CampaignRegistration
from app.models.user import User
from app.schemas.campaign import (
    CampaignCreate,
    CampaignRead,
    CampaignRegistrationRead,
    CampaignUpdate,
)

router = APIRouter(prefix="/admin/campaigns", tags=["admin"])


@router.get("", response_model=list[CampaignRead])
def list_campaigns(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
) -> list[Campaign]:
    return db.query(Campaign).order_by(Campaign.created_at.desc()).all()


@router.post("", response_model=CampaignRead, status_code=201)
def create_campaign(
    payload: CampaignCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Campaign:
    if db.query(Campaign).filter(Campaign.key == payload.key).first():
        raise HTTPException(status_code=409, detail="A campaign with this key already exists")
    campaign = Campaign(**payload.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignRead)
def update_campaign(
    campaign_id: uuid.UUID,
    payload: CampaignUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}/registrations", response_model=list[CampaignRegistrationRead])
def list_registrations(
    campaign_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[CampaignRegistration]:
    if not db.get(Campaign, campaign_id):
        raise HTTPException(status_code=404, detail="Campaign not found")
    return (
        db.query(CampaignRegistration)
        .filter(CampaignRegistration.campaign_id == campaign_id)
        .order_by(CampaignRegistration.created_at.desc())
        .all()
    )
