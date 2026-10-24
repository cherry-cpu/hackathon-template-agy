# Team Parallel Development Guide (5-Member Workflow)

Welcome to the **Synapse AI Content Creator Marketplace** feature engineering sprint!
This guide outlines the zero-conflict, contract-first development workflow so all 5 team members can program simultaneously without blocking each other.

---

## 🚀 1. The Strategy: Contract-First Architecture

We have established **Sidecar Tables**, **Abstract Base Classes**, **Pydantic Schemas**, and **Working Mock Stubs** on `/api/v2/*`. 
- **Frontend (Member 5)** can immediately develop the UI against live endpoints without waiting for backend ML code.
- **Backend Developers (Members 2, 3, 4)** implement their isolated service files without modifying database routing or touching each other's code.
- **Core Lead (Member 1)** ensures continuous integration, DB migrations, and deployment to Render.

---

## 👥 2. 5-Member Role & Ownership Matrix

| Member | Branch Name | Your Target File to Implement | Abstract Interface Contract |
| :--- | :--- | :--- | :--- |
| **Member 1** (Architect & Lead) | `member-1/core-sidecars` | `app/db/database.py`, `app/models/sidecar.py` | Overall orchestration, CI, Render deployment |
| **Member 2** (Semantic Search) | `member-2/semantic-search` | `app/services/embedding_service.py` | `BaseEmbeddingService` in `app/services/interfaces/base_embedding.py` |
| **Member 3** (NER & Hybrid Search) | `member-3/ner-hybrid` | `app/services/ner_service.py`, `app/services/hybrid_search_service.py` | `BaseNERService` in `app/services/interfaces/base_ner.py` |
| **Member 4** (Ranking & RAG) | `member-4/ranking-rag` | `app/services/ranking_service.py`, `app/services/rag_service.py` | `BaseRankingService` & `BaseRAGService` |
| **Member 5** (Frontend UI/UX) | `member-5/frontend-ui` | `frontend/` (or UI components in `app/templates/` & `app/static/`) | Consumes `/api/v2/*` endpoints |

---

## 🛠️ 3. Concrete Member Implementation Instructions

### 👨‍💻 Member 2: Semantic Search & FastEmbed Pipeline
- **Goal**: Implement `BaseEmbeddingService` using **FastEmbed** (`bge-small-en-v1.5` via ONNX).
- **Zero-Budget**: FastEmbed runs locally in Python (<100MB RAM, no GPU, zero API key, zero cost).
- **Steps**:
  1. Create `app/services/embedding_service.py` implementing `BaseEmbeddingService`.
  2. Implement `generate_embedding(text: str) -> List[float]` using `fastembed.TextEmbedding`.
  3. Store float vectors as JSON in `embedding_records` sidecar table.
  4. Implement `compute_similarity(vec_a, vec_b)` using numpy dot product.
  5. Plug into `app/services/advanced_container.py` via `container.set_embedding_service(RealEmbeddingService())`.

### 👨‍💻 Member 3: Named Entity Recognition (NER) & Hybrid Search
- **Goal**: Implement `BaseNERService` and Hybrid Search with Reciprocal Rank Fusion (RRF).
- **Steps**:
  1. Create `app/services/ner_service.py` implementing `BaseNERService`.
  2. Build canonical alias dictionaries (`CANONICAL_TOOLS`, `CANONICAL_FORMATS`, `CANONICAL_LICENSES`).
  3. Use regex matching for instant parsing, with Groq `llama-3.3-70b-versatile` JSON structured fallback.
  4. Always flag provenance: `'creator_claim'` vs `'platform_verified'` vs `'brief_requirement'`.
  5. Implement `reciprocal_rank_fusion` in `app/services/hybrid_search_service.py`.
  6. Plug into `app/services/advanced_container.py`.

### 👨‍💻 Member 4: Ranking Engine & RAG Brief Builder
- **Goal**: Implement `BaseRankingService` and `BaseRAGService`.
- **Steps**:
  1. Create `app/services/ranking_service.py` implementing the 2-Stage Pipeline:
     - **Stage 1 (Hard Gate)**: Exclude creators who lack required commercial buyout rights or required aspect ratio.
     - **Stage 2 (Scoring Formula)**:
       $$\text{Score} = 0.30 \times S_{\text{semantic}} + 0.25 \times S_{\text{tools}} + 0.20 \times S_{\text{style}} + 0.15 \times S_{\text{trust}} + 0.10 \times S_{\text{portfolio}}$$
  2. Create `app/services/rag_service.py` implementing `BaseRAGService`:
     - Fetch grounded portfolio evidence and brief templates from DB.
     - Call Groq LLM with strict Pydantic JSON schema.
     - Enforce zero hallucination: Citations must reference actual portfolio IDs.
  3. Plug into `app/services/advanced_container.py`.

### 👨‍💻 Member 5: Frontend UI Development
- **Goal**: Develop the user interface consuming the `/api/v2/*` endpoints.
- **Immediate APIs Ready To Use (Already Live)**:
  - `POST /api/v2/search/semantic`: Natural language query search.
  - `POST /api/v2/search/hybrid`: Hybrid keyword + vector search with aspect ratio & licensing filters.
  - `POST /api/v2/ner/extract`: Live entity tagger for bio/brief inputs.
  - `POST /api/v2/rankings/creators-for-brief`: Creator ranked leaderboard with match score breakdown modal.
  - `POST /api/v2/briefs/ai-generate`: AI Brief Builder with citations.
  - `GET /api/v2/creators/{id}/explain-match/{job_id}`: Match explainer card with portfolio evidence.

---

## 🧪 4. Testing Your Implementation

Before submitting your PR, verify all tests pass:
```bash
pytest tests/test_advanced_features.py
pytest
```

---

## 🔒 5. Golden Rules for Parallel Work
1. **Never edit files outside your assigned module** without coordinating with Member 1.
2. **Never change the Pydantic schemas** in `app/schemas/advanced.py` without team consensus.
3. **Commit often** to your assigned branch (`member-<N>/...`).
4. **Zero-budget constraint**: Keep all embeddings in-process (FastEmbed) and LLMs on the free Groq tier.
