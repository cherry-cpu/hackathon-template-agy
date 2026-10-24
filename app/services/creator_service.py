from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.creator import CreatorProfile
from app.models.verification import VerificationSignal
from app.schemas.creator import CreatorProfileCreate, CreatorProfileUpdate

class CreatorService:
    @staticmethod
    def get_by_id(db: Session, creator_id: int) -> CreatorProfile | None:
        return db.query(CreatorProfile).filter(CreatorProfile.id == creator_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> CreatorProfile | None:
        return db.query(CreatorProfile).filter(CreatorProfile.user_id == user_id).first()

    @staticmethod
    def create_profile(db: Session, user_id: int, data: CreatorProfileCreate) -> CreatorProfile:
        existing = CreatorService.get_by_user_id(db, user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Creator profile already exists for this user."
            )
        profile = CreatorProfile(
            user_id=user_id,
            display_name=data.display_name,
            headline=data.headline,
            bio=data.bio,
            specialization=data.specialization,
            skills=data.skills,
            tools_models=data.tools_models,
            workflow=data.workflow,
            experience_level=data.experience_level,
            location=data.location,
            profile_image_url=data.profile_image_url
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def update_profile(db: Session, profile: CreatorProfile, data: CreatorProfileUpdate) -> CreatorProfile:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def calculate_completeness(profile: CreatorProfile) -> int:
        """Calculates profile completion percentage."""
        fields = [
            bool(profile.display_name),
            bool(profile.headline),
            bool(profile.bio),
            bool(profile.specialization),
            bool(profile.skills),
            bool(profile.tools_models),
            bool(profile.workflow),
            bool(profile.location),
            len(profile.portfolio_items) > 0,
        ]
        completed = sum(1 for f in fields if f)
        return int((completed / len(fields)) * 100)

    @staticmethod
    def add_verification_badge(
        db: Session, creator_id: int, signal_type: str, badge_name: str, description: str | None = None
    ) -> VerificationSignal:
        signal = VerificationSignal(
            creator_id=creator_id,
            signal_type=signal_type,
            badge_name=badge_name,
            description=description
        )
        db.add(signal)
        # Also mark creator profile verified
        profile = CreatorService.get_by_id(db, creator_id)
        if profile:
            profile.is_verified = True
        db.commit()
        db.refresh(signal)
        return signal

    @staticmethod
    def list_featured(db: Session, limit: int = 6) -> list[CreatorProfile]:
        return db.query(CreatorProfile).order_by(
            CreatorProfile.is_verified.desc(),
            CreatorProfile.created_at.desc()
        ).limit(limit).all()

creator_service = CreatorService()
