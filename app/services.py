# app/services.py

import asyncio
from typing import List, Dict, Optional
from pydantic import ValidationError
import pygeohash 
from . import cache, database, models, llm
from .models import Article, ArticleResponse, LLMQueryAnalysis

DEFAULT_RADIUS = 10  # km
DEFAULT_LIMIT = 5
DEFAULT_SCORE = 0.7

async def enrich_articles_with_summaries(articles: List[Article]) -> List[ArticleResponse]:
    """Takes a list of articles and generates summaries for them concurrently."""
    tasks = [
        llm.summarizer_chain.ainvoke({"title": article.title, "description": article.description})
        for article in articles
    ]
    summaries = await asyncio.gather(*tasks, return_exceptions=True)

    enriched_articles = []
    for i, article in enumerate(articles):
        summary_content = summaries[i].content if not isinstance(summaries[i], Exception) else "Summary not available."
        enriched_articles.append(
            ArticleResponse(**article.dict(), llm_summary=summary_content.strip())
        )
    return enriched_articles


async def process_unified_news_query(
    query: str,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None
) -> Dict:
    """
    Handles a query from start to finish by first analyzing intent with an LLM,
    then fetching and enriching data accordingly.
    """
    llm_response_dict = await llm.query_analyzer_chain.ainvoke({"query": query})
    try:
        analysis = llm.LLMQueryAnalysis(**llm_response_dict)
    except ValidationError as e:
        raise ValueError(f"The LLM returned an invalid data structure. Details: {e}") from e

    articles: List[Article] = []
    intent = analysis.intent

    if intent == 'nearby' and user_lat is not None and user_lon is not None:
        articles = database.fetch_nearby(user_lat, user_lon, DEFAULT_RADIUS, DEFAULT_LIMIT)
    elif intent == 'category' and analysis.category:
        articles = database.fetch_by_category(analysis.category, DEFAULT_LIMIT)
    elif intent == 'source' and analysis.source:
        articles = database.fetch_by_source(analysis.source, DEFAULT_LIMIT)
    elif intent == 'score':
        articles = database.fetch_by_score(DEFAULT_SCORE, DEFAULT_LIMIT)
    else:  # Default to 'search'
        search_term = ' '.join(analysis.entities) if analysis.entities else query
        articles = database.search_by_text(search_term, DEFAULT_LIMIT)

    enriched_articles = await enrich_articles_with_summaries(articles)

    return {"query_analysis": analysis, "articles": enriched_articles}




async def get_news_by_category(category: str, limit: int) -> List[ArticleResponse]:
    articles = database.fetch_by_category(category, limit)
    return await enrich_articles_with_summaries(articles)

async def get_news_by_text(search_term: str, limit: int) -> List[ArticleResponse]:
    articles = database.search_by_text(search_term, DEFAULT_LIMIT)
    return await enrich_articles_with_summaries(articles)

async def get_news_by_source(source: str, limit: int) -> List[ArticleResponse]:
    articles = database.fetch_by_source(source, limit)
    return await enrich_articles_with_summaries(articles)

async def get_news_by_score(min_score: float, limit: int) -> List[ArticleResponse]:
    articles = database.fetch_by_score(min_score, limit)
    return await enrich_articles_with_summaries(articles)

async def get_news_nearby(lat: float, lon: float, radius: float, limit: int) -> List[ArticleResponse]:
    articles = database.fetch_nearby(lat, lon, radius, limit)
    return await enrich_articles_with_summaries(articles)



async def get_trending_news(lat: float, lon: float, radius: float, limit: int) -> List[models.ArticleResponse]:
    """
    Service to fetch and enrich trending articles, now with an in-memory geohash-based cache.
    """
  
    cache_key = f"trending:{pygeohash.encode(lat, lon, precision=6)}:radius:{int(radius)}"

   
    cached_articles = cache.get_from_cache(cache_key)
    if cached_articles is not None:
        return cached_articles

   
    print("[SERVICE] Cache miss, proceeding to calculate trending articles from database...")
    articles = database.get_trending_articles(lat, lon, radius, limit)
    enriched_articles = await enrich_articles_with_summaries(articles)
    cache.set_in_cache(cache_key, enriched_articles)

    return enriched_articles