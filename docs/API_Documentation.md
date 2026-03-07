# Coffee API Documentation

## 1. Overview

This document describes the Coffee API endpoints, request parameters, response formats,
authentication process, and common error codes.

- API base path: `/api/`
- Interactive docs (CoreAPI): `/docs/`
- Content type: `application/json`

## 2. Authentication

Authentication uses **Bearer Token**.

1. Register (`POST /api/auth/register/`) or login (`POST /api/auth/login/`)
2. Receive a token in response
3. Send token in request header:

```http
Authorization: Bearer <token>
```

### 2.1 Auth Endpoints

#### POST /api/auth/register/
Create a new account.

**Request Body**

| Field | Type | Required | Notes |
|---|---|---|---|
| username | string | Yes | Must be unique |
| email | string | Yes | Must be unique |
| password | string | Yes | Minimum 6 characters |

**Example Request**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret123"}'
```

**Example Success Response (201)**

```json
{
  "token": "4de0dbe6...",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2026-03-07T10:00:00Z"
  }
}
```

#### POST /api/auth/login/
Authenticate with username (or email in current implementation) and password.

**Request Body**

| Field | Type | Required |
|---|---|---|
| username | string | Yes |
| password | string | Yes |

**Example Request**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}'
```

**Example Success Response (200)**

```json
{
  "token": "9f84ab12...",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2026-03-07T10:00:00Z"
  }
}
```

#### GET /api/auth/me/
Return current authenticated user.

**Headers**
- `Authorization: Bearer <token>`

**Example Request**

```bash
curl http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer <token>"
```

**Example Success Response (200)**

```json
{
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2026-03-07T10:00:00Z"
  }
}
```

#### POST /api/auth/logout/
Invalidate current token.

**Headers**
- `Authorization: Bearer <token>`

**Example Request**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Authorization: Bearer <token>"
```

**Example Success Response (200)**

```json
{
  "detail": "Logged out."
}
```

---

## 3. Resource Endpoints

All resources are exposed with DRF ViewSets and support standard actions:

- `list` (`GET /resource/`)
- `retrieve` (`GET /resource/{id}/`)
- `create` (`POST /resource/`)
- `update` (`PUT /resource/{id}/`)
- `partial_update` (`PATCH /resource/{id}/`)
- `destroy` (`DELETE /resource/{id}/`)

### 3.1 Users

- Base URL: `/api/users/`

**Response fields**
- `id`, `username`, `email`, `created_at`
- `password_hash` is write-only

### 3.2 Beans

- Base URL: `/api/beans/`
- List filters:
  - `origin`
  - `roast_level`

**Example Filter Request**

```bash
curl "http://127.0.0.1:8000/api/beans/?origin=Kenya&roast_level=Medium"
```

**Response fields**
- `id`, `name`, `origin`, `roast_level`, `flavour_tags`, `created_at`

### 3.3 Recipes

- Base URL: `/api/recipes/`
- List filters:
  - `is_public=true|false|1|0`
  - `bean=<bean_id>`
- `create` requires authentication; `user` is derived from token.

**Response fields**
- `id`, `user`, `bean`, `method`, `water_temp`, `grind_size`, `brew_time`, `description`, `is_public`, `created_at`, `bean_name`, `bean_origin`

**Example Create Request**

```bash
curl -X POST http://127.0.0.1:8000/api/recipes/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"bean":1,"method":"V60","water_temp":92,"grind_size":"Medium-fine","brew_time":180,"description":"Floral and clean","is_public":true}'
```

### 3.4 Brews

- Base URL: `/api/brews/`
- List filters:
  - `recipe=<recipe_id>`
  - `user=<user_id>` (only returns data for same authenticated user)
- Create/update/delete require authentication.
- Update/delete are limited to brew owner.

**Response fields**
- `id`, `user`, `recipe`, `actual_temp`, `actual_time`, `rating`, `notes`, `brewed_at`

**Example Update Request**

```bash
curl -X PATCH http://127.0.0.1:8000/api/brews/5/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"rating":5,"notes":"Best cup this week"}'
```

### 3.5 Reviews

- Base URL: `/api/reviews/`
- List filter:
  - `recipe=<recipe_id>`
- Create requires authentication.

**Response fields**
- `id`, `reviewer`, `recipe`, `rating`, `comment`, `created_at`

### 3.6 Favourites

- Base URL: `/api/favourites/`
- List filters:
  - `user=<user_id>`
  - `recipe=<recipe_id>`
- Create requires authentication.
- Delete is limited to favourite owner.

**Response fields**
- `id`, `user`, `recipe`, `created_at`

---

## 4. Analytics Endpoint

### GET /api/analytics/summary/
Returns aggregate public insights.

**Example Response (200)**

```json
{
  "popular_methods": [
    {"method":"V60","count":12},
    {"method":"AeroPress","count":9}
  ],
  "average_ratings_by_origin": [
    {"origin":"Ethiopia","avg_rating":4.6,"total_reviews":14}
  ],
  "most_favourited_recipes": [
    {"id":7,"method":"V60","bean_id":3,"favourites_count":10,"average_rating":4.7}
  ]
}
```

---

## 5. Common Response Formats

### Success

```json
{
  "id": 1,
  "...": "resource fields"
}
```

or list:

```json
[
  {"id": 1},
  {"id": 2}
]
```

### Error

```json
{
  "detail": "Error message"
}
```

Validation errors may also be field-based:

```json
{
  "rating": ["Ensure this value is less than or equal to 5."]
}
```

---

## 6. Error Codes

| Code | Meaning | Typical Cause |
|---|---|---|
| 200 | OK | Successful read/login/logout/update |
| 201 | Created | Successful create/register |
| 204 | No Content | Successful delete |
| 400 | Bad Request | Missing fields, invalid payload, validation failures |
| 401 | Unauthorized | Missing or invalid token, invalid credentials |
| 403 | Forbidden | Authenticated but not resource owner |
| 404 | Not Found | Resource ID does not exist |
| 405 | Method Not Allowed | HTTP method not supported by endpoint |
| 500 | Internal Server Error | Unexpected server issue |
| 501 | Not Implemented | CoreAPI docs unavailable in incompatible runtime |

---

## 7. Notes

- Current implementation uses token records stored in `user_tokens` table.
- Interactive docs pull descriptions from endpoint/view docstrings.
- For best docs compatibility in this project setup, use Python 3.12.
