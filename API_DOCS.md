# Howzzat Backend — API Documentation

**Base URL:** `https://api.howzzat.pk/api/v1`

All endpoints return `application/json` responses.

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Matches (Local Database)](#2-matches-local-database)
3. [Predictions](#3-predictions)
4. [Leaderboard](#4-leaderboard)
5. [Live Scores (Cricbuzz via RapidAPI)](#5-live-scores-cricbuzz-via-rapidapi)
6. [Matches — Upcoming / Recent / Live (Cricbuzz)](#6-matches--upcoming--recent--live-cricbuzz)
7. [Match Info & Scoreboard (Cricbuzz)](#7-match-info--scoreboard-cricbuzz)
8. [Schedule (Cricbuzz)](#8-schedule-cricbuzz)
9. [Series (Cricbuzz)](#9-series-cricbuzz)
10. [Teams & Players (Cricbuzz)](#10-teams--players-cricbuzz)
11. [Admin — Local Match Update](#11-admin--local-match-update)
12. [Pagination](#12-pagination)
13. [Error Handling](#13-error-handling)

---

## 1. Authentication

### Register a New User

Creates a new user account. At least one of `email` or `mobile_number` is required.

```
POST /api/v1/auth/register/
```

**Request Body:**

| Field           | Type   | Required | Description                                       |
|-----------------|--------|----------|---------------------------------------------------|
| `username`      | string | No       | Desired username. Auto-generated if not provided.  |
| `email`         | string | No*      | User's email address.                              |
| `mobile_number` | string | No*      | User's mobile number.                              |
| `password`      | string | Yes      | Account password.                                  |

> *At least one of `email` or `mobile_number` must be provided.

**Example Request:**
```json
{
  "username": "mehdi",
  "email": "mehdi@howzzat.pk",
  "mobile_number": "+923001234567",
  "password": "securepassword123"
}
```

**Success Response** — `201 Created`:
```json
{
  "status": "success",
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "username": "mehdi",
    "email": "mehdi@howzzat.pk",
    "mobile_number": "+923001234567",
    "leaderboard_points": 0
  }
}
```

**Error Response** — `400 Bad Request`:
```json
{
  "status": "error",
  "message": "A user with this email already exists."
}
```

---

### Login

Authenticates a user using email, mobile number, or username along with their password.

```
POST /api/v1/auth/login/
```

**Request Body:**

| Field           | Type   | Required | Description                                             |
|-----------------|--------|----------|---------------------------------------------------------|
| `identifier`    | string | No*      | Username, email, or mobile number (universal login).     |
| `email`         | string | No*      | User's email address.                                    |
| `mobile_number` | string | No*      | User's mobile number.                                    |
| `password`      | string | Yes      | Account password.                                        |

> *Provide at least one of `identifier`, `email`, or `mobile_number`.

**Example Request:**
```json
{
  "identifier": "mehdi@howzzat.pk",
  "password": "securepassword123"
}
```

**Success Response** — `200 OK`:
```json
{
  "status": "success",
  "message": "Login successful.",
  "user": {
    "id": 1,
    "username": "mehdi",
    "email": "mehdi@howzzat.pk",
    "mobile_number": "+923001234567",
    "leaderboard_points": 500
  }
}
```

**Error Response** — `401 Unauthorized`:
```json
{
  "status": "error",
  "message": "Invalid credentials. Please check your email/mobile number and password."
}
```

---

## 2. Matches (Local Database)

### List All Matches (Paginated)

Returns paginated historical match records from the local database with comprehensive filtering.

```
GET /api/v1/matches/
```

**Query Parameters:**

| Parameter    | Type   | Description                                            |
|--------------|--------|--------------------------------------------------------|
| `page`       | int    | Page number (default: 1)                               |
| `page_size`  | int    | Results per page (default: 20, max: 100)               |
| `search`     | string | Free text search across team names, venue, city, winner |
| `year`       | int    | Filter by match year (e.g., `2024`)                    |
| `match_type` | string | Filter by type: `T20`, `ODI`, `Test`, `IT20`           |
| `team`       | string | Filter by team name (searches both team_a and team_b)  |
| `team_type`  | string | Filter by team type: `international`, `club`           |
| `gender`     | string | Filter by gender: `male`, `female`, `men`, `women`     |
| `venue`      | string | Filter by venue name                                   |
| `city`       | string | Filter by city name                                    |
| `winner`     | string | Filter by winning team name                            |
| `date_from`  | date   | Start date filter (`YYYY-MM-DD`)                       |
| `date_to`    | date   | End date filter (`YYYY-MM-DD`)                         |

**Example Request:**
```
GET /api/v1/matches/?match_type=T20&team=Pakistan&page=1&page_size=10
```

**Success Response** — `200 OK`:
```json
{
  "count": 150,
  "next": "https://api.howzzat.pk/api/v1/matches/?page=2",
  "previous": null,
  "results": [
    {
      "match_id": "1234567",
      "match_type": "T20",
      "team_type": "international",
      "gender": "male",
      "date": "2024-06-15",
      "team_a": "Pakistan",
      "team_b": "India",
      "venue": "Nassau County Ground",
      "city": "New York",
      "winner": "India",
      "margin_runs": 6,
      "margin_wickets": null,
      "prediction_locked": true
    }
  ]
}
```

---

### Get Match Detail

Returns full match details including team rosters and player information.

```
GET /api/v1/matches/{match_id}/
```

**Path Parameters:**

| Parameter  | Type   | Description              |
|------------|--------|--------------------------|
| `match_id` | string | Unique match identifier  |

**Success Response** — `200 OK`:
```json
{
  "match_id": "1234567",
  "match_type": "T20",
  "team_type": "international",
  "gender": "male",
  "date": "2024-06-15",
  "team_a": "Pakistan",
  "team_b": "India",
  "venue": "Nassau County Ground",
  "city": "New York",
  "winner": "India",
  "margin_runs": 6,
  "margin_wickets": null,
  "prediction_locked": true,
  "innings_json": [
    { "team": "Pakistan", "score": "159/7", "overs": "20" },
    { "team": "India", "score": "160/5", "overs": "18.4" }
  ],
  "rosters": [
    {
      "team_name": "Pakistan",
      "player": { "id": "p001", "name": "Babar Azam" }
    }
  ]
}
```

**Error Response** — `404 Not Found`:
```json
{ "detail": "Match not found" }
```

---

### Get Live Score (Redis + Postgres)

Returns live score data from Redis cache (10s TTL) with Postgres fallback.

```
GET /api/v1/matches/{match_id}/live
```

**Success Response** — `200 OK`:
```json
{
  "source": "redis",
  "data": [
    { "team": "Pakistan", "score": "120/3", "overs": "14.2" }
  ]
}
```

---

## 3. Predictions

### Submit a Match Prediction

Place a prediction on a match winner by wagering leaderboard points.

```
POST /api/v1/predict/
```

**Request Body:**

| Field                | Type   | Required | Description                                 |
|----------------------|--------|----------|---------------------------------------------|
| `user_id`            | int    | Yes      | ID of the user making the prediction        |
| `match_id`           | string | Yes      | ID of the match to predict                  |
| `predicted_winner_id`| string | Yes      | Team/player ID of predicted winner           |
| `token_amount`       | int    | Yes      | Number of leaderboard points to wager (> 0) |

**Example Request:**
```json
{
  "user_id": 1,
  "match_id": "1234567",
  "predicted_winner_id": "Pakistan",
  "token_amount": 50
}
```

**Success Response** — `200 OK`:
```json
{
  "message": "Prediction submitted successfully",
  "prediction_id": 42
}
```

**Error Responses:**

| Status | Message                                    |
|--------|--------------------------------------------|
| `400`  | Token amount must be greater than 0        |
| `400`  | Insufficient leaderboard points            |
| `403`  | Predictions for this match are locked      |
| `404`  | Match not found / User not found           |
| `422`  | Validation errors (missing/invalid fields) |

---

## 4. Leaderboard

### Get Top 100 Users

Returns the top 100 users ranked by leaderboard points.

```
GET /api/v1/leaderboard/
```

**Success Response** — `200 OK`:
```json
[
  { "user_id": 1, "username": "mehdi", "points": 1500 },
  { "user_id": 5, "username": "ali_khan", "points": 1200 },
  { "user_id": 3, "username": "cricket_fan", "points": 950 }
]
```

---

## 5. Live Scores (Cricbuzz via RapidAPI)

### Get Live Scores

Returns currently live matches with real-time scores from Cricbuzz.

```
GET /api/v1/rapid/live-scores/
```

**Cache TTL:** 30 seconds

---

## 6. Matches — Upcoming / Recent / Live (Cricbuzz)

### Get Upcoming Matches

```
GET /api/v1/rapid/matches/upcoming/
```
**Cache TTL:** 120 seconds

### Get Recent Matches

```
GET /api/v1/rapid/matches/recent/
```
**Cache TTL:** 120 seconds

### Get Live Matches

```
GET /api/v1/rapid/matches/live/
```
**Cache TTL:** 30 seconds

---

## 7. Match Info & Scoreboard (Cricbuzz)

### Get Match Info

Returns full match metadata: toss, venue, playing XI, series info.

```
GET /api/v1/rapid/match/info/?match_id={match_id}
```

**Query Parameters:**

| Parameter  | Type   | Default  | Description             |
|------------|--------|----------|-------------------------|
| `match_id` | string | `102040` | Cricbuzz match ID       |

**Cache TTL:** 60 seconds

### Get Match Scoreboard

Returns detailed innings scorecard: batting, bowling, fall of wickets.

```
GET /api/v1/rapid/match/scoreboard/?match_id={match_id}
```

**Query Parameters:**

| Parameter  | Type   | Default  | Description             |
|------------|--------|----------|-------------------------|
| `match_id` | string | `102040` | Cricbuzz match ID       |

**Cache TTL:** 30 seconds

---

## 8. Schedule (Cricbuzz)

All schedule endpoints return upcoming match fixtures. The frontend can filter by category client-side.

| Endpoint                                 | Description              |
|------------------------------------------|--------------------------|
| `GET /api/v1/rapid/schedule/`            | All upcoming fixtures    |
| `GET /api/v1/rapid/schedule/international` | International matches  |
| `GET /api/v1/rapid/schedule/league`      | Franchise league matches |
| `GET /api/v1/rapid/schedule/domestic`    | Domestic matches         |
| `GET /api/v1/rapid/schedule/women`       | Women's matches          |
| `GET /api/v1/rapid/schedule/all`         | All categories combined  |

**Cache TTL:** 120 seconds (all schedule endpoints)

---

## 9. Series (Cricbuzz)

All series endpoints return current and upcoming series/tournament listings.

| Endpoint                                | Description               |
|-----------------------------------------|---------------------------|
| `GET /api/v1/rapid/series/`             | All current series        |
| `GET /api/v1/rapid/series/international`| International series      |
| `GET /api/v1/rapid/series/league`       | Franchise league series   |
| `GET /api/v1/rapid/series/domestic`     | Domestic series           |
| `GET /api/v1/rapid/series/women`        | Women's series            |
| `GET /api/v1/rapid/series/all`          | All series combined       |

**Cache TTL:** 300 seconds (all series endpoints)

---

## 10. Teams & Players (Cricbuzz)

### Get International Teams

Returns a list of international cricket teams.

```
GET /api/v1/rapid/teams/
```

**Cache TTL:** 600 seconds

### Get Players by Team

Returns the player squad for a specific team.

```
GET /api/v1/rapid/players/?team_id={team_id}
```

**Query Parameters:**

| Parameter | Type   | Default | Description            |
|-----------|--------|---------|------------------------|
| `team_id` | string | `2`     | Cricbuzz team ID       |

**Cache TTL:** 600 seconds

---

## 11. Admin — Local Match Update

### Update Local Match Score

Admin-only endpoint to push live score updates into the local database and Redis cache. Requires the `X-Admin-Key` header.

```
POST /api/v1/admin/local-match/update
```

**Headers:**

| Header       | Type   | Required | Description          |
|--------------|--------|----------|----------------------|
| `X-Admin-Key`| string | Yes      | Admin API key        |

**Request Body:**

| Field          | Type   | Required | Description                               |
|----------------|--------|----------|-------------------------------------------|
| `match_id`     | string | Yes      | ID of the match to update                 |
| `team`         | string | Yes      | Team name for this innings update         |
| `runs`         | int    | Yes      | Current run total                         |
| `wickets`      | int    | Yes      | Current wickets fallen                    |
| `overs_played` | string | Yes      | Overs bowled (e.g., `"14.3"`)             |
| `match_status` | string | Yes      | `"Live"` or `"Completed"`                 |

**Example Request:**
```bash
curl -X POST https://api.howzzat.pk/api/v1/admin/local-match/update \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: supersecret" \
  -d '{
    "match_id": "1234567",
    "team": "Pakistan",
    "runs": 185,
    "wickets": 4,
    "overs_played": "18.2",
    "match_status": "Live"
  }'
```

**Success Response** — `200 OK`:
```json
{
  "message": "Match updated successfully",
  "data": [
    { "team": "Pakistan", "score": "185/4", "overs": "18.2" }
  ]
}
```

> When `match_status` is `"Completed"`, predictions are automatically settled in the background and `prediction_locked` is set to `true`.

**Error Response** — `401 Unauthorized`:
```json
{ "detail": "Invalid admin API key" }
```

---

## 12. Pagination

All paginated endpoints use the following response format:

```json
{
  "count": 150,
  "next": "https://api.howzzat.pk/api/v1/matches/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

| Parameter   | Default | Max | Description             |
|-------------|---------|-----|-------------------------|
| `page`      | 1       | —   | Page number             |
| `page_size` | 20      | 100 | Number of items per page|

---

## 13. Error Handling

All error responses follow a consistent format:

| HTTP Status | Meaning                    |
|-------------|----------------------------|
| `200`       | Success                    |
| `201`       | Resource created           |
| `400`       | Bad request / Validation   |
| `401`       | Unauthorized (invalid key) |
| `403`       | Forbidden (locked)         |
| `404`       | Resource not found         |
| `422`       | Unprocessable entity       |

**Standard Error Response:**
```json
{ "detail": "Human-readable error message" }
```

---

*Generated for Howzzat Backend v1 — Last updated: August 2026*
