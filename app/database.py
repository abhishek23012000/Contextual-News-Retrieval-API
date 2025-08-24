
import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict
from geopy.distance import geodesic
from .models import Article,UserEvent

DATABASE_PATH = "news_database.db"

def init_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY NOT NULL, title TEXT, description TEXT, url TEXT,
            publication_date TEXT, source_name TEXT, category TEXT,
            relevance_score REAL, latitude REAL, longitude REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_events (
            id TEXT PRIMARY KEY, article_id TEXT, user_id TEXT, event_type TEXT,
            timestamp TEXT, user_lat REAL, user_lon REAL,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
    """)
    conn.commit()
    conn.close()


def add_user_event(event: UserEvent):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM articles WHERE id = ?", (event.article_id,))
    article_exists = cursor.fetchone()
    if not article_exists:
        print(f"[EVENT LOGGING WARNING] Attempted to log event for non-existent article_id: {event.article_id}")
        conn.close()
        return
    cursor.execute(
        "INSERT INTO user_events VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), event.article_id, event.user_id, event.event_type, datetime.now().isoformat(), event.user_lat, event.user_lon)
    )
    conn.commit()
    conn.close()
    print(f"[EVENT LOGGING SUCCESS] Logged '{event.event_type}' for article_id: {event.article_id}")

def get_trending_articles(lat: float, lon: float, radius: float, limit: int) -> List[Article]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    recent_cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    cursor.execute(
        "SELECT article_id, event_type, user_lat, user_lon FROM user_events WHERE timestamp > ?",
        (recent_cutoff,)
    )
    recent_events = cursor.fetchall()
    if not recent_events:
        return []

    trending_scores = defaultdict(float)
    user_location = (lat, lon)
    event_weights = {'click': 3.0, 'view': 1.0, 'share': 5.0}

    for article_id, event_type, event_lat, event_lon in recent_events:
        distance = geodesic(user_location, (event_lat, event_lon)).kilometers
        if distance <= radius:
            geo_weight = (radius - distance) / radius
            base_event_score = event_weights.get(event_type.lower(), 0.5)
            trending_scores[article_id] += (base_event_score * geo_weight)
    
    if not trending_scores:
        return []

    sorted_article_ids = sorted(trending_scores.keys(), key=lambda aid: trending_scores[aid], reverse=True)
    top_ids = sorted_article_ids[:limit]

    final_articles = []
    for article_id in top_ids:
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        if row:
            final_articles.append(_row_to_article(row))
    
    conn.close()
    return final_articles





def load_articles_from_json(file_path: str):
    """
    Loads and replaces articles from a JSON file with robust validation to ensure IDs are present.
    """
    print("\n--- [LOADER] Starting to load articles from JSON ---")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            articles_data = json.load(file)
        print(f"[LOADER] Successfully loaded {len(articles_data)} articles from {file_path}.")
    except Exception as e:
        print(f"[LOADER] CRITICAL FAILURE: Could not read or parse the JSON file. Error: {e}")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("[LOADER] Deleting all existing articles and events from the database...")
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM user_events") 
    
    print("[LOADER] Inserting new articles...")
    successful_inserts = 0
    for i, article_data in enumerate(articles_data):
        article_id = article_data.get('id')

        if not article_id:
            print(f"  -> FATAL WARNING: Article at index {i} (Title: {article_data.get('title')}) has a missing or empty 'id'. SKIPPING.")
            continue

        # print(f"  -> Inserting article {i+1}: ID = '{article_id}', Title = {article_data.get('title')}")
        category_list = article_data.get('category', [])
        cursor.execute(
            "INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(article_id), 
                article_data.get('title'), article_data.get('description'), article_data.get('url'),
                article_data.get('publication_date'), article_data.get('source_name'), json.dumps(category_list),
                article_data.get('relevance_score'), article_data.get('latitude'), article_data.get('longitude')
            )
        )
        successful_inserts += 1
    
    conn.commit()
    conn.close()
    print(f"[LOADER] Finished loading. Successfully inserted {successful_inserts}/{len(articles_data)} articles.")
    print("--- [LOADER] Finished ---\n")


def get_trending_articles(lat: float, lon: float, radius: float, limit: int) -> List[Article]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    recent_cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    cursor.execute(
        "SELECT article_id, event_type, user_lat, user_lon FROM user_events WHERE timestamp > ?",
        (recent_cutoff,)
    )
    recent_events = cursor.fetchall()
    if not recent_events:
        return []

    trending_scores = defaultdict(float)
    user_location = (lat, lon)
    event_weights = {'click': 3.0, 'view': 1.0, 'share': 5.0}


    for article_id, event_type, event_lat, event_lon in recent_events:
        distance = geodesic(user_location, (event_lat, event_lon)).kilometers
        if distance <= radius:
            geo_weight = (radius - distance) / radius
            base_event_score = event_weights.get(event_type.lower(), 0.5)
            trending_scores[article_id] += (base_event_score * geo_weight)
    
    if not trending_scores:
        return []

    sorted_article_ids = sorted(trending_scores.keys(), key=lambda aid: trending_scores[aid], reverse=True)
    top_ids = sorted_article_ids[:limit]

    final_articles = []
    for article_id in top_ids:
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        if row:
            final_articles.append(_row_to_article(row))
    
    conn.close()
    return final_articles

def _row_to_article(row) -> Article:
    return Article(id=row[0], title=row[1], description=row[2], url=row[3],
                   publication_date=row[4], source_name=row[5], category=json.loads(row[6]),
                   relevance_score=row[7], latitude=row[8], longitude=row[9])


def fetch_by_category(category: str, limit: int) -> List[Article]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE category LIKE ? ORDER BY publication_date DESC LIMIT ?", (f'%"{category}"%', limit))
    articles = [_row_to_article(row) for row in cursor.fetchall()]
    conn.close()
    return articles

def fetch_by_source(source: str, limit: int) -> List[Article]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE source_name LIKE ? ORDER BY publication_date DESC LIMIT ?", (f"%{source}%", limit))
    articles = [_row_to_article(row) for row in cursor.fetchall()]
    conn.close()
    return articles

def fetch_by_score(min_score: float, limit: int) -> List[Article]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE relevance_score >= ? ORDER BY relevance_score DESC LIMIT ?", (min_score, limit))
    articles = [_row_to_article(row) for row in cursor.fetchall()]
    conn.close()
    return articles

def search_by_text(query: str, limit: int) -> List[Article]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    search_pattern = f"%{query}%"
    cursor.execute("SELECT * FROM articles WHERE title LIKE ? OR description LIKE ? ORDER BY relevance_score DESC LIMIT ?", (search_pattern, search_pattern, limit))
    articles = [_row_to_article(row) for row in cursor.fetchall()]
    conn.close()
    return articles

def fetch_nearby(lat: float, lon: float, radius: float, limit: int) -> List[Article]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles")
    all_articles = [_row_to_article(row) for row in cursor.fetchall()]
    conn.close()
    user_location = (lat, lon)
    nearby_articles = []
    for article in all_articles:
        distance = geodesic(user_location, (article.latitude, article.longitude)).kilometers
        if distance <= radius:
            nearby_articles.append((article, distance))
    nearby_articles.sort(key=lambda x: x[1])
    return [article for article, dist in nearby_articles[:limit]]