import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.dashboard import DashboardSection, RoleDashboardSection
from app.models.user import User
from app.schemas.dashboard import (
    DashboardSectionCreate,
    DashboardSectionRead,
    DashboardSectionUpdate,
    ResolvedDashboardSection,
    RoleDashboardSectionRead,
    RoleDashboardSectionUpsert,
)

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/sections", response_model=list[ResolvedDashboardSection])
def get_my_dashboard_sections(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[ResolvedDashboardSection]:
    rows = (
        db.query(RoleDashboardSection, DashboardSection)
        .join(DashboardSection, RoleDashboardSection.dashboard_section_id == DashboardSection.id)
        .filter(RoleDashboardSection.role == current_user.role, RoleDashboardSection.enabled.is_(True))
        .order_by(RoleDashboardSection.display_order.asc())
        .all()
    )
    resolved = []
    for role_section, section in rows:
        merged_config = {**(section.default_config or {}), **(role_section.config_override or {})}
        resolved.append(
            ResolvedDashboardSection(
                key=section.key,
                component_key=section.component_key,
                name=section.name,
                config=merged_config,
            )
        )
    return resolved


# --- admin: manage the section catalog ---

admin_router = APIRouter(prefix="/admin/dashboard-sections", tags=["admin"])


@admin_router.get("", response_model=list[DashboardSectionRead])
def list_sections(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
) -> list[DashboardSection]:
    return db.query(DashboardSection).order_by(DashboardSection.name).all()


@admin_router.post("", response_model=DashboardSectionRead, status_code=status.HTTP_201_CREATED)
def create_section(
    payload: DashboardSectionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> DashboardSection:
    if db.query(DashboardSection).filter(DashboardSection.key == payload.key).first():
        raise HTTPException(status_code=409, detail="A section with this key already exists")
    section = DashboardSection(**payload.model_dump())
    db.add(section)
    db.commit()
    db.refresh(section)
    return section


@admin_router.patch("/{section_id}", response_model=DashboardSectionRead)
def update_section(
    section_id: uuid.UUID,
    payload: DashboardSectionUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> DashboardSection:
    section = db.get(DashboardSection, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    db.add(section)
    db.commit()
    db.refresh(section)
    return section


@admin_router.get("/{section_id}/roles", response_model=list[RoleDashboardSectionRead])
def list_section_roles(
    section_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[RoleDashboardSection]:
    return (
        db.query(RoleDashboardSection)
        .filter(RoleDashboardSection.dashboard_section_id == section_id)
        .all()
    )


@admin_router.put("/{section_id}/roles/{role}", response_model=RoleDashboardSectionRead)
def upsert_section_role(
    section_id: uuid.UUID,
    role: str,
    payload: RoleDashboardSectionUpsert,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> RoleDashboardSection:
    from app.models.user import UserRole

    if not db.get(DashboardSection, section_id):
        raise HTTPException(status_code=404, detail="Section not found")
    try:
        role_enum = UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unknown role")

    row = (
        db.query(RoleDashboardSection)
        .filter(
            RoleDashboardSection.dashboard_section_id == section_id,
            RoleDashboardSection.role == role_enum,
        )
        .first()
    )
    if not row:
        row = RoleDashboardSection(dashboard_section_id=section_id, role=role_enum)

    row.enabled = payload.enabled
    row.display_order = payload.display_order
    row.config_override = payload.config_override
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
