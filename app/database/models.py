from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Float, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class JobRecord(Base):
    __tablename__ = "jobs"

    __table_args__ = (
        UniqueConstraint(
            "company",
            "requisition_id",
            name="uq_company_requisition",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    company: Mapped[str] = mapped_column(String(100))
    requisition_id: Mapped[str] = mapped_column(String(150))

    title: Mapped[str] = mapped_column(String(250))
    location: Mapped[str | None] = mapped_column(String(250), nullable=True)

    description: Mapped[str] = mapped_column(Text)

    application_url: Mapped[str] = mapped_column(Text)

    date_posted: Mapped[date | None] = mapped_column(Date, nullable=True)

    date_discovered: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    last_seen: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    alert_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    match_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    application_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )