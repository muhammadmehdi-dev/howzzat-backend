from django.db import models
from django.contrib.auth.hashers import make_password, check_password as django_check_password

class Match(models.Model):
    match_id = models.CharField(max_length=255, primary_key=True)
    match_type = models.CharField(max_length=255, null=True, blank=True)
    team_type = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    team_a = models.CharField(max_length=255, null=True, blank=True)
    team_b = models.CharField(max_length=255, null=True, blank=True)
    venue = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    winner = models.CharField(max_length=255, null=True, blank=True)
    margin_runs = models.IntegerField(null=True, blank=True)
    margin_wickets = models.IntegerField(null=True, blank=True)
    prediction_locked = models.BooleanField(default=False)
    innings_json = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'matches'
        indexes = [
            models.Index(fields=['-date'], name='matches_date_idx'),
            models.Index(fields=['match_type'], name='matches_type_idx'),
            models.Index(fields=['gender'], name='matches_gender_idx'),
            models.Index(fields=['team_a', 'team_b'], name='matches_teams_idx'),
            models.Index(fields=['match_type', '-date'], name='matches_type_date_idx'),
        ]

    def __str__(self):
        return f"{self.match_id} - {self.team_a} vs {self.team_b}"


class Player(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'players'
        indexes = [
            models.Index(fields=['name'], name='players_name_idx'),
        ]

    def __str__(self):
        return self.name


class MatchRoster(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, db_column='match_id', related_name='rosters')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, db_column='player_id', related_name='match_rosters')
    team_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'match_rosters'
        indexes = [
            models.Index(fields=['match', 'team_name'], name='roster_match_team_idx'),
        ]


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    password_hash = models.CharField(max_length=255, null=True, blank=True)
    leaderboard_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'users'

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        if not self.password_hash:
            return False
        return django_check_password(raw_password, self.password_hash)

    def __str__(self):
        return self.username or self.email or self.mobile_number or f"User-{self.id}"


class MatchPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, db_column='match_id')
    predicted_winner_id = models.CharField(max_length=255)
    token_amount = models.IntegerField()
    status = models.CharField(max_length=50, default='Pending')

    class Meta:
        db_table = 'match_predictions'
