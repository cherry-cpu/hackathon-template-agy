from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ==========================================
# 1. Semantic Search Schemas
# ==========================================
class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    entity_type: str = Field("creator", description="Target entity: 'creator' or 'job'")
    top_k: int = Field(10, ge=1, le=50)

class SemanticSearchResultItem(BaseModel):
    entity_id: int
    entity_type: str
    similarity_score: float
    headline: Optional[str] = None
    title: Optional[str] = None
    snippet: Optional[str] = None
    matched_tags: List[str] = []

class SemanticSearchResponse(BaseModel):
    query: str
    results: List[SemanticSearchResultItem]
    total_found: int
    model_used: str

# ==========================================
# 2. Named Entity Recognition (NER) Schemas
# ==========================================
class EntityItem(BaseModel):
    category: str        # 'tool', 'skill', 'style', 'format', 'license', 'budget'
    raw_value: str
    canonical_value: str
    provenance: str      # 'creator_claim' | 'platform_verified' | 'brief_requirement'
    confidence: float

class NERExtractRequest(BaseModel):
    text: str = Field(..., description="Raw text from brief, creator bio, or portfolio description")
    source_type: str = Field("creator_claim", description="Provenance context: 'creator_claim' or 'brief_requirement'")

class NERExtractResponse(BaseModel):
    tools: List[EntityItem] = []
    skills: List[EntityItem] = []
    styles: List[EntityItem] = []
    formats: List[EntityItem] = []
    licensing: List[EntityItem] = []
    metadata: Dict[str, Any] = {}

# ==========================================
# 3. Hybrid Search Schemas
# ==========================================
class HybridSearchRequest(BaseModel):
    query: str = Field(..., description="Keyword or natural language query")
    target: str = Field("creators", description="'creators' or 'jobs'")
    # Structured Hard Filters
    content_type: Optional[str] = None
    aspect_ratio: Optional[str] = None
    commercial_use: Optional[str] = None
    required_tool: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=50)

class HybridSearchCandidate(BaseModel):
    id: int
    title_or_name: str
    rrf_score: float
    vector_rank: Optional[int] = None
    keyword_rank: Optional[int] = None
    skills: List[str] = []
    tools: List[str] = []
    is_verified: bool = False
    commercial_ready: bool = True

class HybridSearchResponse(BaseModel):
    query: str
    candidates: List[HybridSearchCandidate]
    page: int
    page_size: int
    total_count: int
    fusion_algorithm: str = "Reciprocal Rank Fusion (RRF)"

# ==========================================
# 4. Creator-Brief Ranking Schemas
# ==========================================
class MatchScoreBreakdown(BaseModel):
    is_eligible: bool
    exclusion_reason: Optional[str] = None
    total_score: float = Field(..., description="Normalized 0.0 - 100.0")
    semantic_score: float = Field(..., description="Weight 30%")
    tool_overlap_score: float = Field(..., description="Weight 25%")
    style_content_score: float = Field(..., description="Weight 20%")
    trust_signal_score: float = Field(..., description="Weight 15%")
    portfolio_evidence_score: float = Field(..., description="Weight 10%")
    matched_tools: List[str] = []
    missing_tools: List[str] = []
    verified_badges: List[str] = []
    supporting_portfolio_ids: List[int] = []

class RankedCreatorItem(BaseModel):
    creator_id: int
    display_name: str
    specialization: Optional[str] = None
    is_verified: bool
    match_score: float
    breakdown: MatchScoreBreakdown

class BriefRankingRequest(BaseModel):
    job_id: int = Field(..., description="Creative brief / job ID")
    limit: int = Field(20, ge=1, le=100)

class BriefRankingResponse(BaseModel):
    job_id: int
    job_title: str
    ranked_creators: List[RankedCreatorItem]
    total_eligible: int
    total_excluded: int

# ==========================================
# 5. RAG Schemas
# ==========================================
class RAGBriefGenerateRequest(BaseModel):
    rough_idea: str = Field(..., description="Unstructured brand campaign concept")
    company_context: Optional[str] = Field(None, description="Optional brand guidelines or identity notes")

class RAGBriefGenerateResponse(BaseModel):
    title: str
    content_type: str
    style: str
    format: str
    aspect_ratio: str
    commercial_use: str
    required_skills: List[str]
    required_tools: List[str]
    campaign_requirements: str
    budget_range: str
    grounding_citations: List[str] = Field(..., description="References to catalog standards and past briefs used")

class MatchExplanationResponse(BaseModel):
    creator_id: int
    job_id: int
    explanation_narrative: str
    breakdown: MatchScoreBreakdown
    grounded_portfolio_evidence: List[Dict[str, Any]]
