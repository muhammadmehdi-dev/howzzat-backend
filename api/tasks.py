import logging
from django.db import transaction
from .models import Match, MatchPrediction, User

logger = logging.getLogger(__name__)

def settle_completed_match(match_id: str):
    try:
        match = Match.objects.get(match_id=match_id)
    except Match.DoesNotExist:
        logger.error(f"Match {match_id} not found for settlement.")
        return

    official_winner = match.winner

    with transaction.atomic():
        pending_predictions = MatchPrediction.objects.filter(
            match_id=match_id, 
            status='Pending'
        )

        won_predictions = []
        lost_predictions = []

        for prediction in pending_predictions:
            if prediction.predicted_winner_id == official_winner:
                prediction.status = 'Won'
                won_predictions.append(prediction)
                # Refund token amount * 2
                user = prediction.user
                user.leaderboard_points += (prediction.token_amount * 2)
                user.save(update_fields=['leaderboard_points'])
            else:
                prediction.status = 'Lost'
                lost_predictions.append(prediction)

        if won_predictions:
            MatchPrediction.objects.bulk_update(won_predictions, ['status'])
        if lost_predictions:
            MatchPrediction.objects.bulk_update(lost_predictions, ['status'])

        logger.info(f"Settled {len(pending_predictions)} predictions for match {match_id}.")
