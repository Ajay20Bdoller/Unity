import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class GuardianRelationshipStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class GuardianRelationship(Base):
    """A student <-> parent link. A student initiates it (§5); it starts
    PENDING until the parent verifies (or rejects) it. This is identity
    linkage only — whether any *sensitive* feature is actually allowed
    is a separate question answered by ConsentRecord (§6), not by this
    table's status alone.
    """

    __tablename__ = "guardian_relationships"
    __table_args__ = (
        UniqueConstraint("student_id", "parent_id", name="uq_guardian_relationship_pair"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[GuardianRelationshipStatus] = mapped_column(
        Enum(
            GuardianRelationshipStatus,
            name="guardian_relationship_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=GuardianRelationshipStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
