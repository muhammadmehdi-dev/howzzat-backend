from django.contrib import admin
from .models import Match, Player, MatchRoster, User, MatchPrediction

# Customise the Admin Site Headers
admin.site.site_header = "Howzzat Administration"
admin.site.site_title = "Howzzat Admin Portal"
admin.site.index_title = "Welcome to the Howzzat Backend"

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_id', 'match_type', 'team_a', 'team_b', 'date', 'winner', 'prediction_locked')
    search_fields = ('match_id', 'team_a', 'team_b', 'city', 'venue')
    list_filter = ('match_type', 'gender', 'prediction_locked', 'date')
    ordering = ('-date', 'match_id')
    readonly_fields = ('innings_json',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')

@admin.register(MatchRoster)
class MatchRosterAdmin(admin.ModelAdmin):
    list_display = ('id', 'match', 'player', 'team_name')
    search_fields = ('match__match_id', 'player__id', 'player__name', 'team_name')
    list_filter = ('team_name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'leaderboard_points', 'created_at')
    search_fields = ('username', 'email', 'mobile_number')
    list_filter = ('created_at',)
    ordering = ('-leaderboard_points', 'id')
    readonly_fields = ('created_at',)

@admin.register(MatchPrediction)
class MatchPredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'match', 'predicted_winner_id', 'token_amount', 'status')
    search_fields = ('match__match_id', 'predicted_winner_id', 'status', 'user__username')
    list_filter = ('status',)
    ordering = ('id', 'token_amount')
