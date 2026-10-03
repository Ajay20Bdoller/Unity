import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.user import UserRole


class DashboardSection(Base):
    """A known, code-defined dashboard widget. The DB can toggle/order/
    configure these — it can never invent a new one out of thin air.
    `component_key` must match an entry in the frontend's fixed section
    registry (see CLAUDE.md §6); an unknown key must fail safely on the
    frontend, never execute anything database-driven.
    """

    __tablename__ = "dashboard_sections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    component_key: Mapped[str] = mapped_column(String(50), nullable=False)
    default_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DashboardMessage(Base):
    """Admin-authored content shown inside the motivational_quotes_card
    dashboard section (component_key = 'motivational_quotes_card').
    Unlike DashboardSection (which only toggles/orders fixed, code-
    defined widgets), this is actual text content the admin writes and
    edits directly -- a quote, a short message, anything meant to show
    in a rounded card on the dashboard. Whether this section shows at
    all, and to which roles, is still controlled the normal way via
    role_dashboard_sections; this only controls what it says."""

    __tablename__ = "dashboard_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    attribution: Mapped[str | None] = mapped_column(String(150), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RoleDashboardSection(Base):
    """Per-role visibility/ordering/config for a section. Absence of a
    row for a (section, role) pair means "not shown to that role" —
    there's no implicit default-on."""

    __tablename__ = "role_dashboard_sections"
    __table_args__ = (
        UniqueConstraint("dashboard_section_id", "role", name="uq_role_dashboard_section"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    dashboard_section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dashboard_sections.id"), nullable=False, index=True
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    config_override: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
