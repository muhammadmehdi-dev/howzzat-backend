import pytest
from rest_framework.test import APIClient
from api.models import Match, Player, MatchRoster

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_get_matches_list_paginated(api_client):
    for i in range(25):
        Match.objects.create(
            match_id=f"match_{i}",
            match_type="T20",
            team_a="India",
            team_b="Australia",
            date="2026-07-01"
        )
    
    response = api_client.get("/api/v1/matches/")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert data["count"] == 25
    assert len(data["results"]) == 20
    assert "next" in data


@pytest.mark.django_db
def test_get_matches_list_filtering(api_client):
    Match.objects.create(match_id="m1", match_type="T20", team_a="India", team_b="Pakistan")
    Match.objects.create(match_id="m2", match_type="ODI", team_a="Australia", team_b="England")
    
    response = api_client.get("/api/v1/matches/?match_type=T20")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["results"][0]["match_id"] == "m1"
    
    response_team = api_client.get("/api/v1/matches/?team=Australia")
    assert response_team.status_code == 200
    data_team = response_team.json()
    assert data_team["count"] == 1
    assert data_team["results"][0]["match_id"] == "m2"


@pytest.mark.django_db
def test_get_matches_year_and_venue_filters(api_client):
    Match.objects.create(match_id="m_2023", date="2023-05-10", venue="Wankhede Stadium", city="Mumbai", winner="India")
    Match.objects.create(match_id="m_2024", date="2024-06-15", venue="MCG", city="Melbourne", winner="Australia")

    # Filter by year
    res_year = api_client.get("/api/v1/matches/?year=2024")
    assert res_year.status_code == 200
    assert res_year.json()["count"] == 1
    assert res_year.json()["results"][0]["match_id"] == "m_2024"

    # Filter by venue
    res_venue = api_client.get("/api/v1/matches/?venue=Wankhede")
    assert res_venue.status_code == 200
    assert res_venue.json()["count"] == 1
    assert res_venue.json()["results"][0]["match_id"] == "m_2023"

    # Filter by winner
    res_winner = api_client.get("/api/v1/matches/?winner=Australia")
    assert res_winner.status_code == 200
    assert res_winner.json()["count"] == 1
    assert res_winner.json()["results"][0]["match_id"] == "m_2024"


@pytest.mark.django_db
def test_get_match_detail_optimized(api_client, django_assert_num_queries):
    match = Match.objects.create(
        match_id="detail_1",
        match_type="T20",
        team_a="India",
        team_b="Australia"
    )
    p1 = Player.objects.create(id="p1", name="Player 1")
    p2 = Player.objects.create(id="p2", name="Player 2")
    MatchRoster.objects.create(match=match, player=p1, team_name="India")
    MatchRoster.objects.create(match=match, player=p2, team_name="Australia")
    
    # Exactly 3 queries: 1 for Match, 1 for Rosters, 1 for Players (regardless of roster size)
    with django_assert_num_queries(3):
        response = api_client.get(f"/api/v1/matches/{match.match_id}/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["match_id"] == "detail_1"
    assert len(data["rosters"]) == 2
    assert data["rosters"][0]["player"]["name"] in ["Player 1", "Player 2"]
