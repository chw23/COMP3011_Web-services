# COMP3011 Web Services

Coffee brewing and review platform built with Django + Django REST Framework.

## What is included

- REST API for users, beans, recipes, brews, reviews, and favourites
- Token-based authentication endpoints (`/api/auth/...`)
- Analytics summary endpoint (`/api/analytics/summary/`)
- CoreAPI-based interactive API docs (`/docs/`)
- Simple frontend pages for auth, recipes, beans, brew logging, and analytics

## Runtime compatibility

This project currently uses:

- `Django==6.0.2`
- `djangorestframework==3.16.1`
- `coreapi==2.3.3`

Recommended Python version: **3.12**.

Why:

- Django 6.0 requires Python >= 3.12
- CoreAPI has compatibility issues on Python 3.13+ (for example Python 3.14)

## Quick start

### 1) Create and activate a virtual environment (Python 3.12)

```bash
/opt/homebrew/bin/python3.12 -m venv .venv312
source .venv312/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Apply migrations

```bash
python manage.py migrate
```

### 4) Run development server

```bash
python manage.py runserver
```

## Main URLs

### Frontend pages

- `/` (redirects to `/recipes/`)
- `/auth/`
- `/auth/register/`
- `/users/me/`
- `/beans/`
- `/recipes/`
- `/recipes/<recipe_id>/`
- `/recipes/create/`
- `/brews/log/`
- `/analytics/`

### API root

- `/api/`

### API docs

- `/docs/`
- Detailed project documentation PDF: [docs/API_Documentation.pdf](docs/API_Documentation.pdf)
- Markdown source: [docs/API_Documentation.md](docs/API_Documentation.md)

If the runtime cannot load CoreAPI, `/docs/` returns a `501` response with a compatibility message.

## API endpoints

### Authentication

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/auth/me/`
- `POST /api/auth/logout/`

Use header for protected operations:

```http
Authorization: Bearer <token>
```

### Resources (DRF ViewSets)

- `/api/users/`
- `/api/beans/`
- `/api/recipes/`
- `/api/brews/`
- `/api/reviews/`
- `/api/favourites/`

Supported default actions:

- `list` (`GET` collection)
- `retrieve` (`GET` detail)
- `create` (`POST`)
- `update` (`PUT`)
- `partial_update` (`PATCH`)
- `destroy` (`DELETE`)

### Analytics

- `GET /api/analytics/summary/`

Returns:

- most popular brewing methods
- average ratings by bean origin
- most favourited public recipes

## Query parameters currently supported

- `GET /api/beans/?origin=<value>&roast_level=<value>`
- `GET /api/recipes/?is_public=true|false&bean=<bean_id>`
- `GET /api/brews/?recipe=<recipe_id>&user=<user_id>`
- `GET /api/reviews/?recipe=<recipe_id>`
- `GET /api/favourites/?user=<user_id>&recipe=<recipe_id>`

## Ownership and auth behavior

- Creating recipes, brews, reviews, and favourites requires authentication
- Brew updates/deletes are limited to the brew owner
- Favourite delete is limited to the favourite owner
- `/api/auth/me/` and `/api/auth/logout/` require bearer token auth

## Deployment (PythonAnywhere)

The application is deployed at: **https://chw23.pythonanywhere.com**

All API endpoints, frontend pages, and `/docs/` are accessible at that base URL.

### Re-deploying after changes

1. Push changes to the `deploy` branch on GitHub.
2. In a PythonAnywhere Bash console:

```bash
cd ~/COMP3011_Web-services
git pull origin deploy
source venv/bin/activate
pip install -r requirements.txt
DJANGO_DEBUG=False python manage.py migrate
DJANGO_DEBUG=False python manage.py collectstatic --noinput
```

3. Go to the **Web** tab and click **Reload**.

### Production configuration notes

- `DEBUG` is disabled in production (`DJANGO_DEBUG=False` env var).
- Static files are served by [WhiteNoise](https://whitenoise.readthedocs.io/) via `STATIC_ROOT = BASE_DIR / 'staticfiles'`.
- `.pythonanywhere.com` is included in `ALLOWED_HOSTS` automatically when `DEBUG=False`.
- The secret key should be rotated via the `DJANGO_SECRET_KEY` environment variable for production use.

## Notes

- Existing legacy plaintext password hashes are auto-upgraded to Django hashes on successful login.
- API docs descriptions are generated from view/viewset docstrings.
