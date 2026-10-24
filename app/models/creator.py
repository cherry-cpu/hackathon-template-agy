from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    headline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated list
    tools_models: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated list
    workflow: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    user = relationship("User", back_populates="creator_profile")
    portfolio_items = relationship("PortfolioItem", back_populates="creator", cascade="all, delete-orphan", order_by="desc(PortfolioItem.created_at)")
    verification_signals = relationship("VerificationSignal", back_populates="creator", cascade="all, delete-orphan")
    engagements = relationship("Engagement", back_populates="creator", cascade="all, delete-orphan")
    company_views = relationship("CompanyProfileView", back_populates="creator", cascade="all, delete-orphan")

    def skills_list(self) -> list[str]:
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def tools_list(self) -> list[str]:
        if not self.tools_models:
            return []
        return [t.strip() for t in self.tools_models.split(",") if t.strip()]
