
from cachetools import TTLCache

in_memory_cache = TTLCache(maxsize=1000, ttl=300)

def get_from_cache(key: str):
    """Attempts to retrieve an item from our in-memory TTLCache."""
    
    cached_data = in_memory_cache.get(key)
    
    if cached_data:
        print(f"[CACHE] HIT for key: {key}")
        return cached_data 
    
    print(f"[CACHE] MISS for key: {key}")
    return None

def set_in_cache(key: str, value: list):
    """Stores an item in our in-memory TTLCache."""
    
    in_memory_cache[key] = value
    print(f"[CACHE] SET value for key: {key} with TTL: {in_memory_cache.ttl}s")