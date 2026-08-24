from rest_framework import serializers
from .models import User, Match, Player, MatchRoster

class PredictionRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    match_id = serializers.CharField()
    predicted_winner_id = serializers.CharField()
    token_amount = serializers.IntegerField()

class LeaderboardSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id')
    points = serializers.IntegerField(source='leaderboard_points')

    class Meta:
        model = User
        fields = ['user_id', 'username', 'points']

class LocalMatchUpdateSerializer(serializers.Serializer):
    match_id = serializers.CharField()
    team = serializers.CharField()
    runs = serializers.IntegerField()
    wickets = serializers.IntegerField()
    overs_played = serializers.CharField()
    match_status = serializers.CharField()


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name']


class MatchRosterSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = MatchRoster
        fields = ['team_name', 'player']


class MatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            'match_id',
            'match_type',
            'team_type',
            'gender',
            'date',
            'team_a',
            'team_b',
            'venue',
            'city',
            'winner',
            'margin_runs',
            'margin_wickets',
            'prediction_locked'
        ]


class MatchDetailSerializer(serializers.ModelSerializer):
    rosters = MatchRosterSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            'match_id',
            'match_type',
            'team_type',
            'gender',
            'date',
            'team_a',
            'team_b',
            'venue',
            'city',
            'winner',
            'margin_runs',
            'margin_wickets',
            'prediction_locked',
            'innings_json',
            'rosters'
        ]
