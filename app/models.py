from pydantic import BaseModel, Field
from typing import List, Optional

# --- LLM Output Models ---
class LLMQueryAnalysis(BaseModel):
    intent: str = Field(..., description="The primary user intent, one of: 'category', 'source', 'search', 'nearby', 'score'.")
    entities: List[str] = Field(default_factory=list, description="Key entities like 'Elon Musk', 'Twitter'.")
    category: Optional[str] = Field(None, description="The specific news category if mentioned.")
    source: Optional[str] = Field(None, description="The specific news source if mentioned.")
    location: Optional[str] = Field(None, description="The location mentioned for a 'nearby' query.")

# --- Database Models ---
class Article(BaseModel):
    id: str
    title: str
    description: str
    url: str
    publication_date: str
    source_name: str
    category: List[str]
    relevance_score: float
    latitude: float
    longitude: float

# --- API Response Models ---
class ArticleResponse(BaseModel):
    title: str
    description: str
    url: str
    publication_date: str
    source_name: str
    category: List[str]
    relevance_score: float
    llm_summary: str

class NewsApiResponse(BaseModel):
    """The root object for the intelligent /search API response."""
    query_analysis: LLMQueryAnalysis
    articles: List[ArticleResponse]


class ArticleListResponse(BaseModel):
    """A simple list of articles for direct API endpoints."""
    articles: List[ArticleResponse]



class UserEvent(BaseModel):
    """Defines the structure for logging a user interaction event."""
    article_id: str
    user_id: str = Field(..., description="A unique identifier for the user.")
    event_type: str = Field(..., description="The type of event (e.g., 'view', 'click').")
    user_lat: float = Field(..., description="The latitude where the event occurred.")
    user_lon: float = Field(..., description="The longitude where the event occurred.")