import os
import json
import threading
import redis
from django.conf import settings
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Match, User, MatchPrediction
from .pagination import StandardResultsSetPagination
from .serializers import (
    PredictionRequestSerializer,
    LeaderboardSerializer,
    LocalMatchUpdateSerializer,
    MatchListSerializer,
    MatchDetailSerializer
)
from .tasks import settle_completed_match

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


@api_view(['GET'])
def get_matches(request):
    """
    Get paginated match records with comprehensive filtering and fast database indexing.
    Supported Query Parameters:
    - search: Free text search in team names, venue, city, winner, match type
    - year: Filter by match year (e.g., 2024)
    - match_type: Filter by match type (e.g., T20, ODI, Test, IT20)
    - team: Filter by team name (matches team_a or team_b)
    - team_type: Filter by team type (e.g., international, club)
    - venue: Filter by venue name
    - city: Filter by city name
    - winner: Filter by winner team name
    - date_from: Start date filter (YYYY-MM-DD)
    - date_to: End date filter (YYYY-MM-DD)
    """
    queryset = Match.objects.all().order_by('-date', 'match_id')

    # Year filter
    year = request.query_params.get('year')
    if year:
        try:
            queryset = queryset.filter(date__year=int(year))
        except ValueError:
            pass

    # Match type filter
    match_type = request.query_params.get('match_type')
    if match_type:
        queryset = queryset.filter(match_type__iexact=match_type)

    # Team filter
    team = request.query_params.get('team')
    if team:
        queryset = queryset.filter(Q(team_a__icontains=team) | Q(team_b__icontains=team))

    # Team type filter
    team_type = request.query_params.get('team_type')
    if team_type:
        queryset = queryset.filter(team_type__iexact=team_type)

    # Gender filter (male / female / men / women)
    gender = request.query_params.get('gender')
    if gender:
        val = gender.lower()
        if val in ('female', 'women', 'w'):
            queryset = queryset.filter(gender__iexact='female')
        elif val in ('male', 'men', 'm'):
            queryset = queryset.filter(gender__iexact='male')
        else:
            queryset = queryset.filter(gender__iexact=val)

    # Venue filter
    venue = request.query_params.get('venue')
    if venue:
        queryset = queryset.filter(venue__icontains=venue)

    # City filter
    city = request.query_params.get('city')
    if city:
        queryset = queryset.filter(city__icontains=city)

    # Winner filter
    winner = request.query_params.get('winner')
    if winner:
        queryset = queryset.filter(winner__icontains=winner)

    # Date range filters
    date_from = request.query_params.get('date_from')
    if date_from:
        queryset = queryset.filter(date__gte=date_from)

    date_to = request.query_params.get('date_to')
    if date_to:
        queryset = queryset.filter(date__lte=date_to)

    # Free text search filter
    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(
            Q(team_a__icontains=search) |
            Q(team_b__icontains=search) |
            Q(venue__icontains=search) |
            Q(city__icontains=search) |
            Q(winner__icontains=search) |
            Q(match_type__icontains=search)
        )

    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = MatchListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def get_match_detail(request, match_id):
    """
    Get single match details including team rosters and players in 2 optimized queries (solves N+1 problem).
    """
    try:
        match = Match.objects.prefetch_related('rosters__player').get(match_id=match_id)
    except Match.DoesNotExist:
        return Response({"detail": "Match not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = MatchDetailSerializer(match)
    return Response(serializer.data)


@api_view(['POST'])
def make_prediction(request):
    serializer = PredictionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
    req = serializer.validated_data
    
    try:
        match = Match.objects.get(match_id=req['match_id'])
    except Match.DoesNotExist:
        return Response({"detail": "Match not found"}, status=status.HTTP_404_NOT_FOUND)
        
    if match.prediction_locked:
        return Response({"detail": "Predictions for this match are locked"}, status=status.HTTP_403_FORBIDDEN)
        
    try:
        user = User.objects.get(id=req['user_id'])
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
    if user.leaderboard_points < req['token_amount']:
        return Response({"detail": "Insufficient leaderboard points"}, status=status.HTTP_400_BAD_REQUEST)
        
    if req['token_amount'] <= 0:
        return Response({"detail": "Token amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
        
    # Deduct points and save
    user.leaderboard_points -= req['token_amount']
    user.save(update_fields=['leaderboard_points'])
    
    prediction = MatchPrediction.objects.create(
        user=user,
        match=match,
        predicted_winner_id=req['predicted_winner_id'],
        token_amount=req['token_amount'],
        status="Pending"
    )
    
    return Response({"message": "Prediction submitted successfully", "prediction_id": prediction.id})


@api_view(['GET'])
def get_leaderboard(request):
    users = User.objects.order_by('-leaderboard_points')[:100]
    serializer = LeaderboardSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_live_score(request, match_id):
    cached = redis_client.get(f"match_live:{match_id}")
    if cached:
        return Response({"source": "redis", "data": json.loads(cached)})
        
    try:
        match = Match.objects.get(match_id=match_id)
    except Match.DoesNotExist:
        return Response({"detail": "Match not found"}, status=status.HTTP_404_NOT_FOUND)
        
    return Response({"source": "postgres", "data": match.innings_json})


@api_view(['POST'])
def update_local_match(request):
    api_key = request.headers.get('X-Admin-Key')
    expected_key = os.getenv("ADMIN_API_KEY", "supersecret")
    
    if api_key != expected_key:
        return Response({"detail": "Invalid admin API key"}, status=status.HTTP_401_UNAUTHORIZED)
        
    serializer = LocalMatchUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
    req = serializer.validated_data
    
    try:
        match = Match.objects.get(match_id=req['match_id'])
    except Match.DoesNotExist:
        return Response({"detail": "Match not found"}, status=status.HTTP_404_NOT_FOUND)
        
    current_innings = match.innings_json or []
    
    updated = False
    for inn in current_innings:
        if inn.get("team") == req['team']:
            inn["score"] = f"{req['runs']}/{req['wickets']}"
            inn["overs"] = req['overs_played']
            updated = True
            break
            
    if not updated:
        current_innings.append({
            "team": req['team'],
            "score": f"{req['runs']}/{req['wickets']}",
            "overs": req['overs_played']
        })
        
    match.innings_json = current_innings
    
    if req['match_status'] == "Completed":
        match.prediction_locked = True
        
    match.save(update_fields=['innings_json', 'prediction_locked'])
    
    redis_key = f"match_live:{req['match_id']}"
    redis_client.setex(redis_key, 10, json.dumps(current_innings))
    
    if req['match_status'] == "Completed":
        threading.Thread(target=settle_completed_match, args=(req['match_id'],)).start()
        
    return Response({"message": "Match updated successfully", "data": current_innings})


# RapidAPI Integrations
from .services import rapid_api

@api_view(['GET'])
def get_rapid_live_scores(request):
    """Fetch live cricket scores from RapidAPI"""
    data = rapid_api.get_live_scores()
    return Response(data)

@api_view(['GET'])
def get_rapid_series(request):
    """Fetch cricket series list from RapidAPI"""
    data = rapid_api.get_series()
    return Response(data)

@api_view(['GET'])
def get_rapid_series_women(request):
    """Fetch women cricket series list from RapidAPI"""
    data = rapid_api.get_series_women()
    return Response(data)

@api_view(['GET'])
def get_rapid_series_league(request):
    """Fetch franchise league series list from RapidAPI"""
    data = rapid_api.get_series_league()
    return Response(data)

@api_view(['GET'])
def get_rapid_series_domestic(request):
    """Fetch domestic cricket series list from RapidAPI"""
    data = rapid_api.get_series_domestic()
    return Response(data)

@api_view(['GET'])
def get_rapid_series_international(request):
    """Fetch international cricket series list from RapidAPI"""
    data = rapid_api.get_series_international()
    return Response(data)

@api_view(['GET'])
def get_rapid_series_all(request):
    """Fetch all master cricket series list from RapidAPI"""
    data = rapid_api.get_series_all()
    return Response(data)

@api_view(['GET'])
def get_rapid_teams(request):
    """Fetch cricket teams from RapidAPI"""
    data = rapid_api.get_teams()
    return Response(data)

@api_view(['GET'])
def get_rapid_players(request):
    """Fetch players for a team from RapidAPI"""
    team_id = request.query_params.get('team_id', '2')
    data = rapid_api.get_players(team_id=team_id)
    return Response(data)

@api_view(['GET'])
def get_rapid_schedule(request):
    """Fetch cricket schedule/fixtures from RapidAPI"""
    data = rapid_api.get_schedule()
    return Response(data)

@api_view(['GET'])
def get_rapid_schedule_women(request):
    """Fetch women cricket schedule/fixtures from RapidAPI"""
    data = rapid_api.get_schedule_women()
    return Response(data)

@api_view(['GET'])
def get_rapid_schedule_league(request):
    """Fetch league cricket schedule/fixtures from RapidAPI"""
    data = rapid_api.get_schedule_league()
    return Response(data)

@api_view(['GET'])
def get_rapid_schedule_domestic(request):
    """Fetch domestic cricket schedule/fixtures from RapidAPI"""
    data = rapid_api.get_schedule_domestic()
    return Response(data)

@api_view(['GET'])
def get_rapid_schedule_international(request):
    """Fetch international cricket schedule/fixtures from RapidAPI"""
    data = rapid_api.get_schedule_international()
    return Response(data)

@api_view(['GET'])
def get_rapid_schedule_all(request):
    """Fetch all cricket schedule/fixtures from RapidAPI"""
    data = rapid_api.get_schedule_all()
    return Response(data)

@api_view(['GET'])
def get_rapid_match_scoreboard(request):
    """Fetch match detailed scoreboard from RapidAPI"""
    match_id = request.query_params.get('match_id', '102040')
    data = rapid_api.get_match_scoreboard(match_id=match_id)
    return Response(data)

@api_view(['GET'])
def get_rapid_match_info(request):
    """Fetch match metadata and info from RapidAPI"""
    match_id = request.query_params.get('match_id', '102040')
    data = rapid_api.get_match_info(match_id=match_id)
    return Response(data)

@api_view(['GET'])
def get_rapid_matches_upcoming(request):
    """Fetch upcoming matches list from RapidAPI"""
    data = rapid_api.get_matches_upcoming()
    return Response(data)

@api_view(['GET'])
def get_rapid_matches_recent(request):
    """Fetch recent completed matches list from RapidAPI"""
    data = rapid_api.get_matches_recent()
    return Response(data)

@api_view(['GET'])
def get_rapid_matches_live(request):
    """Fetch live ongoing matches list from RapidAPI"""
    data = rapid_api.get_matches_live()
    return Response(data)


@api_view(['POST'])
def register_user(request):
    """
    Registers a new user with Email, Mobile Number, Password, and Username.
    """
    data = request.data
    email = data.get('email', '').strip().lower()
    mobile_number = data.get('mobile_number', '').strip()
    password = data.get('password', '')
    username = data.get('username', '').strip()

    if not password:
        return Response({
            "status": "error",
            "message": "Password is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    if not email and not mobile_number:
        return Response({
            "status": "error",
            "message": "Either email or mobile_number is required for registration."
        }, status=status.HTTP_400_BAD_REQUEST)

    if not username:
        if email:
            username = email.split('@')[0]
        else:
            username = f"user_{mobile_number[-4:] if len(mobile_number) >= 4 else '123'}"

    # Check existing user credentials
    if email and User.objects.filter(email=email).exists():
        return Response({
            "status": "error",
            "message": "A user with this email already exists."
        }, status=status.HTTP_400_BAD_REQUEST)

    if mobile_number and User.objects.filter(mobile_number=mobile_number).exists():
        return Response({
            "status": "error",
            "message": "A user with this mobile number already exists."
        }, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        # Append unique suffix if username exists
        import random
        username = f"{username}_{random.randint(100, 999)}"

    user = User(
        username=username,
        email=email if email else None,
        mobile_number=mobile_number if mobile_number else None,
        leaderboard_points=0
    )
    user.set_password(password)
    user.save()

    return Response({
        "status": "success",
        "message": "User registered successfully.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "mobile_number": user.mobile_number,
            "leaderboard_points": user.leaderboard_points
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_user(request):
    """
    Logs in user using either Email OR Mobile Number (or Username) along with Password.
    """
    data = request.data
    identifier = data.get('identifier', '').strip()
    email = data.get('email', '').strip().lower()
    mobile_number = data.get('mobile_number', '').strip()
    password = data.get('password', '')

    target_identity = identifier or email or mobile_number

    if not target_identity or not password:
        return Response({
            "status": "error",
            "message": "Please provide an email/mobile number/identifier and password."
        }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(
        Q(email__iexact=target_identity) | 
        Q(mobile_number=target_identity) | 
        Q(username__iexact=target_identity)
    ).first()

    if not user or not user.check_password(password):
        return Response({
            "status": "error",
            "message": "Invalid credentials. Please check your email/mobile number and password."
        }, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        "status": "success",
        "message": "Login successful.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "mobile_number": user.mobile_number,
            "leaderboard_points": user.leaderboard_points
        }
    }, status=status.HTTP_200_OK)




