import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SiteRegistration(Base):
    __tablename__ = "site_registrations"
    __table_args__ = (
        UniqueConstraint("email", name="uq_site_registrations_email"),
        UniqueConstraint("numeric_key", name="uq_site_registrations_numeric_key"),
        Index("ix_site_registrations_created_at", "created_at"),
        Index("ix_site_registrations_status", "status"),
        Index("ix_site_registrations_email", "email"),
        Index("ix_site_registrations_numeric_key", "numeric_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    adult18: Mapped[str | None] = mapped_column(String(3), nullable=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    participant_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    track: Mapped[str | None] = mapped_column(String(32), nullable=True)
    transport: Mapped[str] = mapped_column(String(64), nullable=False)
    car_number: Mapped[str | None] = mapped_column(String(24), nullable=True)
    passport: Mapped[str] = mapped_column(Text, nullable=False)
    numeric_key: Mapped[str] = mapped_column(String(6), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
