from fastapi import FastAPI, HTTPException, Query, Body, APIRouter
from typing import Optional
from . import services, database, models

app = FastAPI(
    title="Contextual News Retrieval API",
    description="An API with both a single intelligent endpoint and multiple direct endpoints.",
    version="1.2.0"
)

router = APIRouter(prefix="/api/v1/news")

# @app.on_event("startup")
# def on_startup():
#     """Initialize the database and load data on application startup."""
#     database.init_database()
#     database.load_articles_from_json("news_data.json")


@router.get(
    "/", 
    response_model=models.NewsApiResponse,
    summary="Get news using a single, intelligent query"
)
async def get_unified_news(
    query: str = Query(..., description="User's natural language query"),
    lat: Optional[float] = Query(None, description="User's latitude for 'nearby' queries."),
    lon: Optional[float] = Query(None, description="User's longitude for 'nearby' queries.")
):
    """
    Used for automatically understand the user's
    intent (category, source, location, etc.) from a single query string and
    returns the most relevant articles.
    """
    try:
        if ("near" in query.lower() or "around" in query.lower()) and not (lat and lon):
             raise HTTPException(
                status_code=400,
                detail="Location parameters (lat, lon) are required for 'nearby' queries."
            )
        result = await services.process_unified_news_query(query, lat, lon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


@router.get(
    "/category",
    response_model=models.ArticleListResponse,
    summary="Retrieve articles from a specific category"
)
async def get_by_category(
    name: str = Query(..., description="The category to search for (e.g., 'Technology', 'Business')."),
    limit: int = Query(services.DEFAULT_LIMIT, description="Number of articles to return.")
):
    articles = await services.get_news_by_category(name, limit)
    return {"articles": articles}

@router.get(
    "/source",
    response_model=models.ArticleListResponse,
    summary="Retrieve articles from a specific source"
)
async def get_by_source(
    name: str = Query(..., description="The news source to search for (e.g., 'Reuters', 'New York Times')."),
    limit: int = Query(services.DEFAULT_LIMIT, description="Number of articles to return.")
):
    articles = await services.get_news_by_source(name, limit)
    return {"articles": articles}

@router.get(
    "/search",
    response_model=models.ArticleListResponse,
    summary="Retrieve articles from a query"
)
async def get_by_text(
    search_term: str = Query(..., description="Tell me about Elon Musk"),
    limit: int = Query(services.DEFAULT_LIMIT, description="Number of articles to return.")
):
    articles = await services.get_news_by_text(search_term, limit)
    return {"articles": articles}

@router.get(
    "/nearby",
    response_model=models.ArticleListResponse,
    summary="Retrieve articles published near a location"
)

async def get_nearby(
    lat: float = Query(..., description="User's latitude."),
    lon: float = Query(..., description="User's longitude."),
    radius: float = Query(services.DEFAULT_RADIUS, description="Radius in kilometers."),
    limit: int = Query(services.DEFAULT_LIMIT, description="Number of articles to return.")
):
    articles = await services.get_news_nearby(lat, lon, radius, limit)
    return {"articles": articles}

@router.get(
    "/score",
    response_model=models.ArticleListResponse,
    summary="Retrieve articles based on a minimum relevance score"
)
async def get_by_score(
    min_score: float = Query(services.DEFAULT_SCORE, description="The minimum relevance score (e.g., 0.7)."),
    limit: int = Query(services.DEFAULT_LIMIT, description="Number of articles to return.")
):
    articles = await services.get_news_by_score(min_score, limit)
    return {"articles": articles}


@app.post(
    "/api/v1/events",
    status_code=201,
    summary="Log a user interaction event"
)
async def log_user_event(event: models.UserEvent):
    """
    Receives and logs a user event (e.g., a 'view' or 'click') to be used
    by the trending news algorithm.
    """
    try:
        database.add_user_event(event)
        return {"message": "Event logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log event: {str(e)}")

@router.get(
    "/trending",
    response_model=models.ArticleListResponse,
    summary="Get location-based trending news"
)
async def get_trending(
    lat: float = Query(..., description="User's latitude."),
    lon: float = Query(..., description="User's longitude."),
    radius: float = Query(20, description="Radius in kilometers to search for trends (e.g., 20)."),
    limit: int = Query(services.DEFAULT_LIMIT, description="Number of articles to return.")
):
    """
    Returns a list of trending news articles tailored to the user's location.
    The ranking is based on recent user engagement (views, clicks) that
    occurred within the specified radius.
    """
    articles = await services.get_trending_news(lat, lon, radius, limit)
    return {"articles": articles}

app.include_router(router)

    

