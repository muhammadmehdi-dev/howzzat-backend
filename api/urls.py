from django.urls import path
from . import views

urlpatterns = [
    path('matches/', views.get_matches),
    path('matches/<str:match_id>/', views.get_match_detail),
    path('matches/<str:match_id>/live', views.get_live_score),
    path('predict/', views.make_prediction),
    path('leaderboard/', views.get_leaderboard),
    path('admin/local-match/update', views.update_local_match),
    
    # Auth Endpoints
    path('auth/register/', views.register_user),
    path('auth/login/', views.login_user),
    
    # RapidAPI Endpoints
    path('rapid/live-scores/', views.get_rapid_live_scores),
    path('rapid/series/', views.get_rapid_series),
    path('rapid/series/women', views.get_rapid_series_women),
    path('rapid/series/league', views.get_rapid_series_league),
    path('rapid/series/domestic', views.get_rapid_series_domestic),
    path('rapid/series/international', views.get_rapid_series_international),
    path('rapid/series/all', views.get_rapid_series_all),
    path('rapid/teams/', views.get_rapid_teams),
    path('rapid/players/', views.get_rapid_players),
    path('rapid/schedule/', views.get_rapid_schedule),
    path('rapid/schedule/women', views.get_rapid_schedule_women),
    path('rapid/schedule/league', views.get_rapid_schedule_league),
    path('rapid/schedule/domestic', views.get_rapid_schedule_domestic),
    path('rapid/schedule/international', views.get_rapid_schedule_international),
    path('rapid/schedule/all', views.get_rapid_schedule_all),
    path('rapid/match/scoreboard/', views.get_rapid_match_scoreboard),
    path('rapid/match/info/', views.get_rapid_match_info),
    path('rapid/matches/upcoming/', views.get_rapid_matches_upcoming),
    path('rapid/matches/recent/', views.get_rapid_matches_recent),
    path('rapid/matches/live/', views.get_rapid_matches_live),
]
