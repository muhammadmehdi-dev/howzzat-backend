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
    path('rapid/series/archives/', views.get_rapid_series_archives),
    path('rapid/series/<str:series_id>/matches/', views.get_rapid_series_info),
    path('rapid/series/<str:series_id>/news/', views.get_rapid_series_news),
    path('rapid/series/<str:series_id>/squads/', views.get_rapid_series_squads),
    path('rapid/series/<str:series_id>/venues/', views.get_rapid_series_venues),
    path('rapid/series/<str:series_id>/points-table/', views.get_rapid_series_points_table),
    path('rapid/series/<str:series_id>/stats/', views.get_rapid_series_stats_filters),
    path('rapid/series/<str:series_id>/stats/<str:stats_type>/', views.get_rapid_series_stats),
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
    path('rapid/teams/<str:team_id>/schedule/', views.get_rapid_team_schedule),
    path('rapid/teams/<str:team_id>/results/', views.get_rapid_team_results),
    path('rapid/teams/<str:team_id>/news/', views.get_rapid_team_news),
    path('rapid/teams/<str:team_id>/stats/<str:stats_type>/', views.get_rapid_team_stats),
    
    path('rapid/players/trending/', views.get_rapid_trending_players),
    path('rapid/players/search/', views.search_rapid_players),
    path('rapid/players/<str:player_id>/career/', views.get_rapid_player_career),
    path('rapid/players/<str:player_id>/news/', views.get_rapid_player_news),
    path('rapid/players/<str:player_id>/bowling/', views.get_rapid_player_bowling_stats),
    path('rapid/players/<str:player_id>/batting/', views.get_rapid_player_batting_stats),
    
    path('rapid/venues/<str:venue_id>/info/', views.get_rapid_venue_info),
    path('rapid/venues/<str:venue_id>/stats/', views.get_rapid_venue_stats),
    path('rapid/venues/<str:venue_id>/matches/', views.get_rapid_venue_matches),
    
    path('rapid/match/<str:match_id>/team/', views.get_rapid_match_team),
    path('rapid/match/<str:match_id>/overs/', views.get_rapid_match_overs),
    path('rapid/match/<str:match_id>/leanback/', views.get_rapid_match_leanback),
]
