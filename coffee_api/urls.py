"""
URL configuration for coffee_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def _get_docs_urlpatterns():
    try:
        from rest_framework.documentation import include_docs_urls

        return [
            path(
                'docs/',
                include_docs_urls(
                    title='Coffee API',
                    description='API documentation for the Coffee Review service.',
                    public=False,
                ),
            ),
        ]
    except Exception as exc:
        return [
            path(
                'docs/',
                lambda request, error=str(exc): HttpResponse(
                    (
                        'CoreAPI docs are unavailable in the current runtime. '
                        'This usually happens with Python 3.13+ because coreapi '
                        'depends on removed stdlib modules. '
                        f'Underlying error: {error}'
                    ),
                    status=501,
                    content_type='text/plain',
                ),
            ),
        ]
from coffee.views import (
    frontend_home,
    frontend_auth,
    frontend_register,
    frontend_user_profile,
    frontend_beans,
    frontend_recipes,
    frontend_recipe_detail,
    frontend_create_recipe,
    frontend_log_brew,
    frontend_analytics,
)

urlpatterns = [
    path('', frontend_home, name='frontend-home'),
    path('auth/', frontend_auth, name='frontend-auth'),
    path('auth/register/', frontend_register, name='frontend-register'),
    path('users/me/', frontend_user_profile, name='frontend-user-profile'),
    path('beans/', frontend_beans, name='frontend-beans'),
    path('recipes/', frontend_recipes, name='frontend-recipes'),
    path('recipes/<int:recipe_id>/', frontend_recipe_detail, name='frontend-recipe-detail'),
    path('recipes/create/', frontend_create_recipe, name='frontend-create-recipe'),
    path('brews/log/', frontend_log_brew, name='frontend-log-brew'),
    path('analytics/', frontend_analytics, name='frontend-analytics'),
    path('admin/', admin.site.urls),
    path('api/', include('coffee.urls')),
]

urlpatterns += _get_docs_urlpatterns()
