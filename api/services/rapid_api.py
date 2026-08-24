import os
import requests
import hashlib
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────
# Cricbuzz Cricket API (via RapidAPI)
# Host: cricbuzz-cricket.p.rapidapi.com
# ─────────────────────────────────────────────────
BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"


def get_headers():
    api_key = os.getenv("RAPIDAPI_KEY", "970470d838mshbfd3ca44e512643p190672jsn2f5d540443dc")
    api_host = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")
    return {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host,
        "Content-Type": "application/json"
    }


def fetch_rapid_api(endpoint: str, params: dict = None, cache_ttl: int = 60):
    """
    Executes a secure GET request to the Cricbuzz RapidAPI with fallback caching.
    Cache TTL is in seconds. Responses are keyed by a hash of endpoint + params.
    """
    raw_key = f"{endpoint}:{str(params)}"
    hashed_key = hashlib.md5(raw_key.encode('utf-8')).hexdigest()
    cache_key = f"cricbuzz_{hashed_key}"

    cached_response = cache.get(cache_key)
    if cached_response is not None:
        return cached_response

    url = f"{BASE_URL}{endpoint}"
    headers = get_headers()

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Cache response to optimise performance and prevent rate limiting
        cache.set(cache_key, data, cache_ttl)
        return data
    except Exception as e:
        logger.error(f"Cricbuzz RapidAPI fetch error for {endpoint}: {e}")
        return {"error": str(e), "endpoint": endpoint}


# ─────────────────────────────────────────────────
# Matches
# ─────────────────────────────────────────────────

def get_matches_upcoming():
    """All upcoming matches across all categories."""
    return fetch_rapid_api("/matches/v1/upcoming", cache_ttl=120)


def get_matches_recent():
    """Recently completed matches with scores and result."""
    return fetch_rapid_api("/matches/v1/recent", cache_ttl=120)


def get_matches_live():
    """Currently live matches with live scores."""
    return fetch_rapid_api("/matches/v1/live", cache_ttl=30)


# ─────────────────────────────────────────────────
# Schedule aliases (keep existing Django URL routes intact)
# Cricbuzz returns all categories in one endpoint.
# The frontend filters by matchType (International /
# League / Domestic) on the client side.
# ─────────────────────────────────────────────────

def get_schedule():
    return get_matches_upcoming()


def get_schedule_international():
    return get_matches_upcoming()


def get_schedule_league():
    return get_matches_upcoming()


def get_schedule_domestic():
    return get_matches_upcoming()


def get_schedule_women():
    return get_matches_upcoming()


def get_schedule_all():
    return get_matches_upcoming()


# ─────────────────────────────────────────────────
# Match Detail & Scorecard
# ─────────────────────────────────────────────────

def get_match_info(match_id: str = "163013"):
    """Full match metadata: toss, venue, playing XI, series."""
    return fetch_rapid_api(f"/mcenter/v1/{match_id}", cache_ttl=60)


def get_match_scoreboard(match_id: str = "163013"):
    """Detailed innings scorecard: batting, bowling, fall of wickets."""
    return fetch_rapid_api(f"/mcenter/v1/{match_id}/scard", cache_ttl=30)


def get_match_commentary(match_id: str = "163013"):
    """Ball-by-ball commentary for a match."""
    return fetch_rapid_api(f"/mcenter/v1/{match_id}/comm", cache_ttl=30)


# ─────────────────────────────────────────────────
# Series / Tournaments
# ─────────────────────────────────────────────────

def get_series():
    """List of all current/upcoming series."""
    return fetch_rapid_api("/series/v1/list", cache_ttl=300)


def get_series_women():
    return fetch_rapid_api("/series/v1/list", cache_ttl=300)


def get_series_league():
    return fetch_rapid_api("/series/v1/list", cache_ttl=300)


def get_series_domestic():
    return fetch_rapid_api("/series/v1/list", cache_ttl=300)


def get_series_international():
    return fetch_rapid_api("/series/v1/list", cache_ttl=300)


def get_series_all():
    return fetch_rapid_api("/series/v1/list", cache_ttl=300)


def get_series_info(series_id: str):
    """Stats and match list for a specific series/tournament."""
    return fetch_rapid_api(f"/series/v1/{series_id}", cache_ttl=300)


# ─────────────────────────────────────────────────
# Live Scores
# ─────────────────────────────────────────────────

def get_live_scores():
    """Live match listings (backward-compat alias for get_matches_live)."""
    return get_matches_live()


# ─────────────────────────────────────────────────
# News
# ─────────────────────────────────────────────────

def get_news():
    """Latest cricket news articles from Cricbuzz."""
    return fetch_rapid_api("/news/v1/index", cache_ttl=300)


# ─────────────────────────────────────────────────
# Players & Teams
# ─────────────────────────────────────────────────

def get_teams():
    """List of international cricket teams."""
    return fetch_rapid_api("/teams/v1/international", cache_ttl=600)


def get_players(team_id: str = "2"):
    """Players for a specific team."""
    return fetch_rapid_api(f"/teams/v1/{team_id}/players", cache_ttl=600)


def get_player_info(player_id: str):
    """Detailed profile and career stats for a player."""
    return fetch_rapid_api(f"/players/v1/{player_id}", cache_ttl=600)
