# Synapse — AI Content Creator Marketplace

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-45%20Passed-success)](#automated-testing)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An AI-native creative talent marketplace connecting specialized **AI content creators** (filmmakers, animators, prompt engineers, and generative media specialists) with **brands, creative agencies, and enterprises**.

---

## 1. Project Mission & Problem Solved

Traditional freelancer platforms fail to capture the nuances of generative media workflows:
- They lack attributes for **AI-specific models and tools** (e.g., Runway Gen-3, Midjourney v6, Kling AI, Flux.1, ComfyUI pipelines).
- They lack structured specifications for **aspect ratios** (16:9, 9:16 vertical reels, 1:1, 4:5), **content formats**, and **commercial usage buyouts**.
- Creators struggle to communicate proprietary **generative pipelines and workflows** (storyboarding, prompt matrices, spatial/temporal upscaling).

**Synapse Marketplace** solves this through:
1. **AI-Native Creator Profiles & Verification**: Highlighting tools, prompt workflows, specialization, and transparent verification trust signals.
2. **Searchable AI Portfolios**: Upload multi-format media with rich metadata (content type, aspect ratio, models used, prompt engineering notes).
3. **Structured Creative Briefs**: Standardized campaign specifications covering commercial rights, deliverable formats, and required toolchains.
4. **Deterministic Multi-Attribute Discovery**: Real-time filtering across skills, tools, content types, and aspect ratios with guaranteed fallback.
5. **Direct Creator Selection & Engagement**: End-to-end proposal workflow from discovery to hire.
6. **AI Creative Brief Builder (Groq)**: Instant conversion of rough project concepts into structured briefs with automatic fallback when AI services are offline.

---

## 2. High-Level Architecture

```text
Browser / Client (HTML5, Bootstrap 5, Vanilla JS)
        |
        v
FastAPI Web & REST API Layer (Session & Bearer Auth)
        |
        +--------------------------------+
        |                                |
        v                                v
Service Layer                   File Storage Service
(Auth, Creator, Portfolio,       (/uploads/creators/<id>/<safe_name>)
 Search, Job, Engagement)
        |                                |
        +---------------+                |
        |               |                |
        v               v                v
SQLAlchemy ORM    Groq LLM Service    Filesystem
        |         (Graceful Fallback)
        v
Relational DB
(SQLite Dev / MySQL Production)
```

---

## 3. Technology Stack

- **Backend**: Python 3.13, FastAPI (ASGI)
- **Database & ORM**: SQLAlchemy 2.0 (configured for SQLite and MySQL portability)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons
- **AI Integration**: Groq SDK (`llama-3.3-70b-versatile`) with structured JSON schema enforcement and zero-dependency deterministic fallback
- **Authentication**: Bcrypt password hashing + PyJWT signed tokens (supporting both Bearer API headers and secure HTTP-only cookies)
- **File Storage**: Local filesystem adapter with path-traversal prevention, filename sanitization, and MIME-type validation
- **Testing**: pytest, FastAPI TestClient, in-memory SQLite isolation

---

## 4. Quick Start & Local Setup

### Prerequisites
- Python 3.10+ installed
- Git

### 1. Clone & Enter Directory
```bash
git clone <repo-url>
cd v1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional)* Add your Groq API key in `.env` if you wish to use live Groq generation for the AI Brief Builder:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```
> **Note**: The entire marketplace, including the AI Brief Builder, functions seamlessly even without a Groq API key due to built-in intelligent fallback templates.

### 4. Initialize Database & Seed Demo Data
```bash
python -m app.db.seed
```
This sets up realistic demo data: verified AI directors, animators, rich portfolio media with SVG previews, active creative briefs, and engagements.

### 5. Run the Application Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open your browser at:
- **Web Interface**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 5. Demo Walkthrough Credentials

| Role | Email | Password | What You Can Demo |
| :--- | :--- | :--- | :--- |
| **Creator** | `elena@aicreator.io` | `creator123` | View portfolio, upload work with aspect ratios/tools, manage profile completeness, accept brand proposals |
| **Company** | `creative@omnisport.com` | `company123` | Create briefs, use AI brief builder, search & filter creators, send project engagements |
| **Agency** | `director@luminacreative.com` | `company123` | Multi-brief management, social video campaigns |

---

## 6. Core Features & User Journeys

### 1. Creator Portfolio Experience
- Creators upload media (video, animations, photos, graphics) up to 50MB.
- Attach rich metadata: Content Type, Aspect Ratio (`16:9`, `9:16`, `1:1`, `4:5`, `21:9`), Output Format (`MP4`, `PNG`, etc.), AI Tools (`Runway Gen-3`, `Midjourney v6`, `Kling AI`), Skills, and Production Workflow.
- Universal modal preview with embedded media player.

### 2. Multi-Attribute Creator Discovery & Filtering
- Search across text queries (names, bios, portfolio titles).
- Structured filters: Specialization, Tool/Model, Content Type, Aspect Ratio, Format.
- Predictable and combinable (e.g. `Specialization=AI Video` + `Tool=Runway` + `Aspect Ratio=16:9`).
- Informative empty-state handling with one-click filter reset.

### 3. Structured Creative Briefs
- Companies publish briefs with campaign requirements, aspect ratio constraints, required toolchains, and commercial buyout terms.
- Status management: `draft`, `published`, `closed`.

### 4. Creator Engagement & Selection Flow
- Companies can engage a creator directly from their public profile or portfolio work.
- Proposal status cycle: `pending` -> `accepted` / `declined` -> `completed`.
- Full authorization enforcement on both client and server.

### 5. AI Brief Builder (Groq API + Safe Fallback)
- Input: Rough creative concept (e.g. *"I need a short AI video campaign for a new sports shoe"*).
- Output: Structured JSON draft with title, description, deliverables, recommended tools, and licensing terms.
- User review & edit: AI suggestions remain fully editable before saving as an official brief.
- Reliability: Works with or without external AI service uptime.

---

## 7. Automated Testing

The project includes an automated test suite with **45 unit, API, integration, and UI tests** using an isolated in-memory SQLite database:

```bash
python -m pytest -v
```

### Test Coverage Highlights:
- **Authentication**: Registration, password hashing, JWT tokens, duplicate account rejection, role checks.
- **Creator Profiles**: CRUD operations, ownership verification, profile completeness calculation.
- **Portfolios**: File upload validation, disallowed extension rejection (`.exe`), metadata persistence, file cleanup on delete.
- **Creative Briefs**: Posting, validation, commercial buyout terms, ownership checks.
- **Search & Discovery**: Keyword matching, tool filters, aspect ratio filters, case-normalization, empty results.
- **Engagements**: Outbound proposals, status updates, cross-user authorization.
- **File Security**: Filename sanitization, path traversal prevention (`../../etc/passwd`).
- **AI Builder**: Mocked Groq response verification + zero-dependency fallback template tests.
- **Web Routes**: End-to-end HTML template rendering for all pages.

---

## 8. Database Portability (SQLite to MySQL)

The architecture is strictly designed for seamless migration from SQLite to MySQL:
- All database operations utilize SQLAlchemy 2.0 ORM query primitives.
- Portable data types (`String`, `Integer`, `Text`, `Boolean`, `DateTime`) are used across all models.
- Database connection string is environment-driven via `DATABASE_URL`.

To connect to MySQL in production:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/synapse_marketplace
```

---

## 9. Security Principles

1. **Authentication & Authorization**: Server-side JWT validation; protected endpoints enforce role and ownership checks.
2. **File Upload Hardening**:
   - Files are stored in creator-partitioned subdirectories (`/uploads/creators/<id>/`).
   - Filenames are sanitized via regex and unique UUID prefixes.
   - Directory traversal attempts are blocked via path resolution boundary checks.
   - Dangerous file types are rejected via extension whitelist.
3. **Secret Protection**: API keys and secrets reside strictly in environment variables and are excluded from source control via `.gitignore`.
4. **Parameterized Queries**: All database queries are handled through SQLAlchemy ORM, eliminating SQL injection vulnerabilities.
