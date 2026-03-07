from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, BeanViewSet, RecipeViewSet,
    BrewViewSet, ReviewViewSet, FavouriteViewSet, analytics_summary,
    auth_register, auth_login, auth_me, auth_logout,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'beans', BeanViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'brews', BrewViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'favourites', FavouriteViewSet)

urlpatterns = [
    path('auth/register/', auth_register, name='auth-register'),
    path('auth/login/', auth_login, name='auth-login'),
    path('auth/me/', auth_me, name='auth-me'),
    path('auth/logout/', auth_logout, name='auth-logout'),
    path('analytics/summary/', analytics_summary, name='analytics-summary'),
    path('', include(router.urls)),
]
