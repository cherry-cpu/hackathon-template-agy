import os
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, init_db
from app.models.user import User
from app.models.creator import CreatorProfile
from app.models.portfolio import PortfolioItem
from app.models.company import CompanyProfile
from app.models.job import Job
from app.models.verification import VerificationSignal
from app.models.engagement import Engagement
from app.services.auth_service import AuthService
from app.config import settings
from app.services.embedding_service import embedding_service
from app.services.ner_service import ner_service

def seed_advanced_indexes(db: Session) -> None:
    """Indexes all creators, jobs, and portfolios into sidecar embedding and NER tables."""
    try:
        creators = db.query(CreatorProfile).all()
        for c in creators:
            text = f"{c.display_name} {c.headline or ''} {c.bio or ''} {c.specialization or ''} {c.skills or ''} {c.tools_models or ''} {c.workflow or ''}"
            embedding_service.index_entity(db, "creator", c.id, text)
            extracted = ner_service.extract_entities(text, "creator_claim")
            ner_service.persist_extracted_entities("creator", c.id, extracted, db)

        jobs = db.query(Job).all()
        for j in jobs:
            text = f"{j.title} {j.description} {j.campaign_requirements or ''} {j.content_type or ''} {j.style or ''} {j.format or ''} {j.aspect_ratio or ''} {j.required_skills or ''} {j.required_tools or ''} {j.commercial_use or ''}"
            embedding_service.index_entity(db, "job", j.id, text)
            extracted = ner_service.extract_entities(text, "brief_requirement")
            ner_service.persist_extracted_entities("job", j.id, extracted, db)

        portfolios = db.query(PortfolioItem).all()
        for p in portfolios:
            text = f"{p.title} {p.description or ''} {p.workflow or ''} {p.tools_models or ''} {p.skills or ''} {p.tags or ''} {p.content_type or ''} {p.aspect_ratio or ''}"
            embedding_service.index_entity(db, "portfolio", p.id, text)

        print("Advanced sidecar indexes (Embeddings & NER) successfully generated!")
    except Exception as e:
        print(f"Notice: Indexing completed with note: {e}")

def seed_database(db: Session | None = None) -> None:
    should_close = False
    if db is None:
        init_db()
        db = SessionLocal()
        should_close = True

    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            from app.models.sidecar import EmbeddingRecord
            if db.query(EmbeddingRecord).count() == 0:
                seed_advanced_indexes(db)
            return

        print("Seeding initial marketplace data...")

        # Create dummy sample media files for realistic portfolio preview
        uploads_dir = Path(settings.UPLOAD_DIR)
        sample_creator_1_dir = uploads_dir / "creators" / "1"
        sample_creator_2_dir = uploads_dir / "creators" / "2"
        sample_creator_3_dir = uploads_dir / "creators" / "3"
        sample_creator_1_dir.mkdir(parents=True, exist_ok=True)
        sample_creator_2_dir.mkdir(parents=True, exist_ok=True)
        sample_creator_3_dir.mkdir(parents=True, exist_ok=True)

        # SVG placeholder helper
        def write_svg_preview(path: Path, title: str, subtitle: str, bg_color: str = "#1e1e2f"):
            svg = f"""<svg width="640" height="360" xmlns="http://www.w3.org/2000/svg">
                <rect width="100%" height="100%" fill="{bg_color}"/>
                <circle cx="320" cy="180" r="100" fill="#6366f1" opacity="0.3"/>
                <text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" font-weight="bold" fill="#ffffff">{title}</text>
                <text x="50%" y="60%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#a5b4fc">{subtitle}</text>
            </svg>"""
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)

        file_1 = sample_creator_1_dir / "nike_spec.svg"
        file_2 = sample_creator_1_dir / "future_motors.svg"
        file_3 = sample_creator_2_dir / "cyberpunk_loop.svg"
        file_4 = sample_creator_3_dir / "luxury_perfume.svg"

        write_svg_preview(file_1, "Nike Velocity Cinematic", "Runway Gen-3 • 16:9 • AI Video", "#0f172a")
        write_svg_preview(file_2, "Future Motors Teaser", "Kling AI + Midjourney • 16:9", "#111827")
        write_svg_preview(file_3, "Cyberpunk Metropolis", "AnimateDiff • 16:9 • Animation", "#1e1b4b")
        write_svg_preview(file_4, "Aura Luxury Editorial", "Midjourney v6 • 1:1 • Commercial", "#312e81")

        # 1. Creators
        c1_user = User(
            email="elena@aicreator.io",
            password_hash=AuthService.hash_password("creator123"),
            role="creator"
        )
        c2_user = User(
            email="marcus@aicreator.io",
            password_hash=AuthService.hash_password("creator123"),
            role="creator"
        )
        c3_user = User(
            email="aria@aicreator.io",
            password_hash=AuthService.hash_password("creator123"),
            role="creator"
        )
        c4_user = User(
            email="devon@aicreator.io",
            password_hash=AuthService.hash_password("creator123"),
            role="creator"
        )

        # 2. Companies
        comp1_user = User(
            email="creative@omnisport.com",
            password_hash=AuthService.hash_password("company123"),
            role="company"
        )
        comp2_user = User(
            email="director@luminacreative.com",
            password_hash=AuthService.hash_password("company123"),
            role="company"
        )

        db.add_all([c1_user, c2_user, c3_user, c4_user, comp1_user, comp2_user])
        db.commit()

        # Creator Profiles
        c1_profile = CreatorProfile(
            user_id=c1_user.id,
            display_name="Elena Rostova",
            headline="AI Commercial Filmmaker & Generative Director",
            bio="Award-winning filmmaker utilizing cutting-edge diffusion and video transformers (Runway Gen-3, Kling, Sora) to create cinematic advertising.",
            specialization="AI Video",
            skills="AI Video Generation, Prompt Engineering, Motion Design, Storyboarding, Color Grading",
            tools_models="Runway Gen-3, Kling AI, Topaz Video AI, Midjourney v6",
            workflow="1. Moodboard & Prompt bible in Midjourney. 2. Motion orchestration with Runway Gen-3 / Kling. 3. Topaz 4K spatial upscaling. 4. Sound & pacing mastering in DaVinci Resolve.",
            experience_level="Expert (5+ yrs commercial experience)",
            location="Berlin / Remote",
            profile_image_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&auto=format&fit=crop&q=80",
            is_verified=True
        )

        c2_profile = CreatorProfile(
            user_id=c2_user.id,
            display_name="Marcus Vance",
            headline="Generative 3D Worldbuilder & AI Animator",
            bio="Specializing in surreal and sci-fi aesthetic animation with consistent character pipelines.",
            specialization="AI Animation",
            skills="AI Animation, Character Consistency, 3D Camera Projection, ComfyUI Workflows",
            tools_models="Stable Diffusion XL, ComfyUI, AnimateDiff, Blender",
            workflow="Node-based ComfyUI custom pipelines with ControlNet depth maps combined with 3D Blender camera tracking.",
            experience_level="Advanced",
            location="San Francisco / Remote",
            profile_image_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&auto=format&fit=crop&q=80",
            is_verified=True
        )

        c3_profile = CreatorProfile(
            user_id=c3_user.id,
            display_name="Aria Chen",
            headline="Luxury Generative Brand Designer & Art Director",
            bio="Crafting photo-real product photography and key visuals for fashion and beauty houses.",
            specialization="Generative Advertising",
            skills="Product Photography, Lighting Control, Inpainting, Brand Identity",
            tools_models="Midjourney v6, Flux.1, Stable Diffusion XL, Photoshop",
            workflow="Iterative latent space exploration, LoRA training for bespoke product geometries, custom lighting passes.",
            experience_level="Expert",
            location="New York / Remote",
            profile_image_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=300&auto=format&fit=crop&q=80",
            is_verified=True
        )

        c4_profile = CreatorProfile(
            user_id=c4_user.id,
            display_name="Devon Brooks",
            headline="AI Social Content Creator & Growth Hook Specialist",
            bio="Helping DTC brands produce high-converting 9:16 vertical video hooks and dynamic organic creatives.",
            specialization="Social Media Creatives",
            skills="Short-form Video, Hook Pacing, ElevenLabs Voice AI, Rapid Iteration",
            tools_models="Runway Gen-3, Pika Labs, Midjourney v6, ElevenLabs",
            workflow="Trend scraping, AI script generation, vertical asset synthesis, and viral sound sync.",
            experience_level="Intermediate",
            location="London / Remote",
            profile_image_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&auto=format&fit=crop&q=80",
            is_verified=False
        )

        db.add_all([c1_profile, c2_profile, c3_profile, c4_profile])
        db.commit()

        # Portfolios
        p1 = PortfolioItem(
            creator_id=c1_profile.id,
            title="Nike Velocity: Synthetic Athlete Teaser",
            description="Spec commercial directed entirely with generative video pipelines showcasing impossible camera moves.",
            file_path="/uploads/creators/1/nike_spec.svg",
            original_filename="nike_spec.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Video",
            aspect_ratio="16:9",
            format="MP4",
            tools_models="Runway Gen-3, Midjourney v6, Topaz Video AI",
            skills="AI Video Generation, Prompt Engineering, Motion Design",
            specialization="AI Video",
            tags="Commercial, Sports, Futuristic, 4K",
            workflow="Prompt exploration -> Runway Gen-3 camera control -> Topaz upscaling."
        )

        p2 = PortfolioItem(
            creator_id=c1_profile.id,
            title="Future Motors: Hyper-EV Reveal",
            description="Concept automobile launch video with realistic volumetric lighting and dynamic reflections.",
            file_path="/uploads/creators/1/future_motors.svg",
            original_filename="future_motors.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Video",
            aspect_ratio="16:9",
            format="MP4",
            tools_models="Kling AI, Midjourney v6",
            skills="AI Video Generation, Lighting Control",
            specialization="AI Video",
            tags="Automotive, Launch, Luxury",
            workflow="Image-to-video workflow using photoreal Midjourney hero frames."
        )

        p3 = PortfolioItem(
            creator_id=c2_profile.id,
            title="Neo-Shinjuku 2099 Loop",
            description="Infinite seamless cybernetic street animation loop with consistent characters.",
            file_path="/uploads/creators/2/cyberpunk_loop.svg",
            original_filename="cyberpunk_loop.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Animation",
            aspect_ratio="16:9",
            format="MP4",
            tools_models="Stable Diffusion XL, ComfyUI, AnimateDiff",
            skills="AI Animation, Character Consistency",
            specialization="AI Animation",
            tags="Cyberpunk, Loop, SciFi",
            workflow="Multi-ControlNet depth + openpose with AnimateDiff motion model."
        )

        p4 = PortfolioItem(
            creator_id=c3_profile.id,
            title="Aura L'Eau: Luxury Fragrance Key Visuals",
            description="Global perfume campaign visuals featuring crystalline water refraction and botanical flourishes.",
            file_path="/uploads/creators/3/luxury_perfume.svg",
            original_filename="luxury_perfume.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Image",
            aspect_ratio="1:1",
            format="PNG",
            tools_models="Midjourney v6, Flux.1",
            skills="Product Photography, Lighting Control",
            specialization="Generative Advertising",
            tags="Luxury, Perfume, Cosmetics, Studio",
            workflow="Custom stylized prompt matrices with in-painted typography zones."
        )

        db.add_all([p1, p2, p3, p4])

        # Verification Signals
        v1 = VerificationSignal(
            creator_id=c1_profile.id,
            signal_type="tool_verified",
            badge_name="Runway Gen-3 Master",
            description="Verified mastery in generative video camera movement and motion prompting."
        )
        v2 = VerificationSignal(
            creator_id=c1_profile.id,
            signal_type="commercial_ready",
            badge_name="Commercial Grade Verified",
            description="Delivers broadcast-compliant 4K assets with cleared IP rights."
        )
        v3 = VerificationSignal(
            creator_id=c2_profile.id,
            signal_type="tool_verified",
            badge_name="ComfyUI Specialist",
            description="Verified technical proficiency in repeatable node-based generative workflows."
        )
        v4 = VerificationSignal(
            creator_id=c3_profile.id,
            signal_type="commercial_ready",
            badge_name="Luxury Brand Approved",
            description="Demonstrated high-end editorial and commercial product rendering."
        )

        db.add_all([v1, v2, v3, v4])

        # Company Profiles
        comp1 = CompanyProfile(
            user_id=comp1_user.id,
            company_name="OmniSport Global",
            industry="Athletic Apparel & Footwear",
            description="Global leader in performance athletics and street fashion.",
            website="https://omnisport.example.com",
            location="Beaverton, OR / Global",
            tags="Footwear, Apparel, Sports, Innovation"
        )
        comp2 = CompanyProfile(
            user_id=comp2_user.id,
            company_name="Lumina Creative Agency",
            industry="Creative Production & Advertising",
            description="Boutique creative studio producing next-generation brand campaigns for global innovators.",
            website="https://luminacreative.example.com",
            location="London / New York",
            tags="Agency, Advertising, Brand, Production"
        )

        db.add_all([comp1, comp2])
        db.commit()

        # Jobs / Creative Briefs
        j1 = Job(
            company_id=comp1.id,
            title="Cinematic AI Video Campaign: Quantum Sneaker Launch",
            description="We are seeking an elite AI Video Director to create a 30-second hero commercial introducing the Quantum-1 running shoe. The video must feature surreal gravity-defying urban environments and high-velocity motion.",
            campaign_requirements="1. 30s Master Video in 16:9 4K.\n2. Three 10s cutdowns for Instagram/TikTok (9:16).\n3. Storyboard review prior to final render.\n4. Full commercial buyout.",
            content_type="Video",
            style="Cinematic & Hyper-Realistic",
            format="MP4",
            aspect_ratio="16:9",
            commercial_use="Full Commercial Buyout",
            required_skills="AI Video Generation, Prompt Engineering, Motion Design",
            required_tools="Runway Gen-3, Kling AI, Topaz Video AI",
            specialization="AI Video",
            budget_range="$4,000 - $7,000",
            status="published"
        )

        j2 = Job(
            company_id=comp2.id,
            title="Generative Social Video Hooks: Energy Drink Campaign",
            description="Looking for an AI content creator to design 10 punchy, high-energy 9:16 vertical video concepts for a new zero-sugar beverage.",
            campaign_requirements="Fast pacing, eye-catching visual hooks in the first 2 seconds, synchronized sound effects.",
            content_type="Video",
            style="High-Energy Social Hook",
            format="MP4",
            aspect_ratio="9:16",
            commercial_use="Digital & Social Media Buyout",
            required_skills="Short-form Video, Hook Pacing, Sound Design",
            required_tools="Runway, Midjourney, Pika Labs",
            specialization="Social Media Creatives",
            budget_range="$2,500 - $4,500",
            status="published"
        )

        j3 = Job(
            company_id=comp2.id,
            title="Surreal Sci-Fi 3D Environment Backgrounds",
            description="Seeking an AI artist capable of generating 5 seamless looping ambient scifi backgrounds for a live-stream event.",
            campaign_requirements="Seamless looping, 16:9 60fps output, anime/cyberpunk aesthetic.",
            content_type="Animation",
            style="Stylized Cyberpunk",
            format="MP4",
            aspect_ratio="16:9",
            commercial_use="Online Live Event Rights",
            required_skills="AI Animation, 3D Camera Projection",
            required_tools="Stable Diffusion XL, ComfyUI, AnimateDiff",
            specialization="AI Animation",
            budget_range="$1,500 - $3,000",
            status="published"
        )

        db.add_all([j1, j2, j3])
        db.commit()

        # Initial sample engagement
        eng1 = Engagement(
            company_id=comp1.id,
            creator_id=c1_profile.id,
            job_id=j1.id,
            status="pending",
            message="Hi Elena, your 'Nike Velocity' portfolio item completely blew us away. We would love to collaborate with you on our upcoming Quantum Sneaker hero film. Would you be available over the next 3 weeks?",
            proposed_budget="$5,500"
        )
        db.add(eng1)
        db.commit()

        print("Database successfully seeded with realistic marketplace data!")
        seed_advanced_indexes(db)

    finally:
        if should_close:
            db.close()

if __name__ == "__main__":
    seed_database()
