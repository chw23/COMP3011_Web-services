# COMP3011_Web-services
## API Documentation

### Base URL

All routes are mounted under:

`/api`

Example: `POST /api/users`

---

## Authentication & Users

### Create account

- **Endpoint:** `POST /api/users`
- **Body:**

```json
{
	"username": "alice",
	"email": "alice@example.com",
	"password": "secret123"
}
```

- **Response (201):** user object (without password hash)

### Login

- **Endpoint:** `POST /api/auth/login`
- **Body:**

```json
{
	"username": "alice",
	"password": "secret123"
}
```

- **Response (200):** session-based login success and basic user profile

### Logout

- **Endpoint:** `POST /api/auth/logout`
- **Body:** none
- **Response (200):** logout success message

### Add to favourite

- **Endpoint:** `POST /api/users/{id}/favourites`
- **Body:**

```json
{
	"recipe_id": 10
}
```

- Also accepts `recipe` as key.

### Unfavourite

- **Endpoint:** `DELETE /api/users/{id}/favourites/{recipe_id}`
- **Body:** none
- **Response (204):** deleted

### Feed recommendation engine (preferences)

- **Endpoint:** `GET /api/users/{id}/preferences`
- **Response fields:**
	- `user_id`
	- `preferred_origins`
	- `preferred_methods`
	- `avg_review_rating`
	- `avg_brew_rating`
	- `favourite_count`

---

## Beans

### See all beans

- **Endpoint:** `GET /api/beans`

### See specific bean

- **Endpoint:** `GET /api/beans/{id}`

### Filter beans

- **Endpoint:** `GET /api/beans`
- **Query params (optional):**
	- `origin` (exact match, case-insensitive)
	- `roast_level` (exact match, case-insensitive)
	- `name` (contains, case-insensitive)

Example: `GET /api/beans?origin=Ethiopia&roast_level=Medium`

---

## Recipes

### Create recipe

- **Endpoint:** `POST /api/recipes`
- **Body (example):**

```json
{
	"user": 1,
	"bean": 2,
	"method": "Pour Over",
	"water_temp": 92,
	"grind_size": "Medium",
	"brew_time": 180,
	"description": "Balanced and sweet",
	"is_public": true
}
```

### Read recipes

- **Endpoint:** `GET /api/recipes`

### Update recipe

- **Endpoint:** `PUT /api/recipes/{id}`
- **Body:** full recipe payload

### Delete recipe

- **Endpoint:** `DELETE /api/recipes/{id}`

---

## Reviews

### Review a recipe

- **Endpoint:** `POST /api/recipes/{id}/reviews`
- **Body (example):**

```json
{
	"reviewer": 1,
	"rating": 5,
	"comment": "Excellent clarity and sweetness"
}
```

### Read community reviews

- **Endpoint:** `GET /api/recipes/{id}/reviews`

---

## Recommendations

### Recommendation pushing

- **Endpoint:** `GET /api/recommendations`
- **Optional query param:** `user_id`

Examples:
- `GET /api/recommendations` (global/top recommendations)
- `GET /api/recommendations?user_id=1` (personalized when possible)

---

## Brews

### Update notes or rating on an existing brew log

- **Endpoint:** `PATCH /api/brews/{id}`
- **Body (example):**

```json
{
	"rating": 4,
	"notes": "Slightly over-extracted, adjust grind coarser next time"
}
```

---

## Common status codes

- `200 OK` success
- `201 Created` resource created
- `204 No Content` deleted
- `400 Bad Request` invalid payload
- `401 Unauthorized` invalid login
- `404 Not Found` resource missing

## Notes

- Login/logout currently use **session-based** auth.
- Password is accepted as `password` when creating/updating users and stored as a secure hash internally.
