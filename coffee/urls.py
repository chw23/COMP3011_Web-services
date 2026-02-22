from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, BeanViewSet, RecipeViewSet,
    BrewViewSet, ReviewViewSet, FavouriteViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'beans', BeanViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'brews', BrewViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'favourites', FavouriteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
