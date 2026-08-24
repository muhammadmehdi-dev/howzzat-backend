import os
import json
import logging
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Match, Player, MatchRoster

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

JSON_DIR = Path(os.path.expanduser("~/Downloads/all_json"))
BATCH_SIZE = 500

class Command(BaseCommand):
    help = 'Ingest historical match data'

    def handle(self, *args, **options):
        if not JSON_DIR.exists():
            logger.error(f"Directory {JSON_DIR} does not exist.")
            return

        all_files = list(JSON_DIR.glob("*.json"))
        total_files = len(all_files)
        logger.info(f"Found {total_files} JSON files to process.")

        for i in range(0, total_files, BATCH_SIZE):
            batch_files = all_files[i:i + BATCH_SIZE]
            logger.info(f"Processing batch {i//BATCH_SIZE + 1} / {(total_files + BATCH_SIZE - 1) // BATCH_SIZE}")
            self.process_batch(batch_files)

        logger.info("Ingestion completed.")

    def parse_file(self, filepath: Path):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            info = data.get("info", {})
            innings_data = data.get("innings", [])
            
            match_id = filepath.stem
            match_type = info.get("match_type")
            team_type = info.get("team_type")
            gender = info.get("gender")
            
            dates = info.get("dates", [])
            date_obj = datetime.strptime(dates[0], "%Y-%m-%d").date() if dates else None
            
            teams = info.get("teams", [])
            team_a = teams[0] if len(teams) > 0 else None
            team_b = teams[1] if len(teams) > 1 else None
            
            venue = info.get("venue")
            city = info.get("city")
            
            outcome = info.get("outcome", {})
            winner = outcome.get("winner", "Draw/No Result")
            by = outcome.get("by", {})
            margin_runs = by.get("runs")
            margin_wickets = by.get("wickets")
            
            innings_summary = []
            for inn in innings_data:
                team = inn.get("team")
                overs = inn.get("overs", [])
                
                total_runs = 0
                total_wickets = 0
                last_over_str = "0"
                
                for over in overs:
                    over_num = over.get("over", 0)
                    deliveries = over.get("deliveries", [])
                    
                    for d in deliveries:
                        total_runs += d.get("runs", {}).get("total", 0)
                        total_wickets += len(d.get("wickets", []))
                        
                    last_over_str = f"{over_num}.{len(deliveries)}"
                    
                score_str = f"{total_runs}/{total_wickets}"
                
                innings_summary.append({
                    "team": team,
                    "score": score_str,
                    "overs": last_over_str
                })
                
            match = Match(
                match_id=match_id,
                match_type=match_type,
                team_type=team_type,
                gender=gender,
                date=date_obj,
                team_a=team_a,
                team_b=team_b,
                venue=venue,
                city=city,
                winner=winner,
                margin_runs=margin_runs,
                margin_wickets=margin_wickets,
                prediction_locked=True,
                innings_json=innings_summary
            )
            
            people = info.get("registry", {}).get("people", {})
            players = []
            for name, pid in people.items():
                players.append(Player(id=pid, name=name))
                
            rosters = []
            players_map = info.get("players", {})
            for team_name, roster_names in players_map.items():
                for name in roster_names:
                    pid = people.get(name)
                    if pid:
                        rosters.append(MatchRoster(
                            match_id=match_id,
                            player_id=pid,
                            team_name=team_name
                        ))
                        
            return match, players, rosters
        except Exception as e:
            logger.error(f"Error parsing {filepath.name}: {e}")
            return None, [], []

    def process_batch(self, files: list[Path]):
        matches_to_insert = []
        players_to_insert = []
        rosters_to_insert = []
        
        for f in files:
            match, players, rosters = self.parse_file(f)
            if match:
                matches_to_insert.append(match)
            players_to_insert.extend(players)
            rosters_to_insert.extend(rosters)
            
        with transaction.atomic():
            if players_to_insert:
                Player.objects.bulk_create(players_to_insert, ignore_conflicts=True)
            if matches_to_insert:
                Match.objects.bulk_create(
                    matches_to_insert,
                    update_conflicts=True,
                    update_fields=['gender'],
                    unique_fields=['match_id']
                )
            if rosters_to_insert:
                MatchRoster.objects.bulk_create(rosters_to_insert, ignore_conflicts=True)
