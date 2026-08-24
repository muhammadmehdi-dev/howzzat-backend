from django.contrib import admin
from .models import Match, Player, MatchRoster, User, MatchPrediction

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_id', 'match_type', 'team_a', 'team_b', 'date', 'winner')
    search_fields = ('match_id', 'team_a', 'team_b', 'city', 'venue')
    ordering = ('-date', 'match_id')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')

@admin.register(MatchRoster)
class MatchRosterAdmin(admin.ModelAdmin):
    list_display = ('id', 'match_id', 'player_id', 'team_name')
    search_fields = ('match__match_id', 'player__id', 'team_name')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'leaderboard_points')
    search_fields = ('username',)
    ordering = ('-leaderboard_points', 'id')

@admin.register(MatchPrediction)
class MatchPredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'match_id', 'predicted_winner_id', 'token_amount', 'status')
    search_fields = ('match__match_id', 'predicted_winner_id', 'status')
    ordering = ('id', 'token_amount')
