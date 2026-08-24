import pytest
from rest_framework.test import APIClient
from api.models import Match, User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_predict_locked_match_returns_403(api_client):
    Match.objects.create(match_id="test_locked", prediction_locked=True)
    
    payload = {
        "user_id": 1,
        "match_id": "test_locked",
        "predicted_winner_id": "Team A",
        "token_amount": 10
    }
    
    response = api_client.post("/api/v1/predict/", data=payload, format='json')
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Predictions for this match are locked"
