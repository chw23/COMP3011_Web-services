from django.urls import path
from .views import (
    UserCreateView,
    LoginView,
    LogoutView,
    BeanListView,
    BeanDetailView,
    RecipeListCreateView,
    RecipeDetailView,
    RecipeReviewView,
    UserFavouriteView,
    UserFavouriteDetailView,
    UserPreferencesView,
    RecommendationView,
    BrewPartialUpdateView,
)

urlpatterns = [
    path('users', UserCreateView.as_view()),
    path('auth/login', LoginView.as_view()),
    path('auth/logout', LogoutView.as_view()),
    path('beans', BeanListView.as_view()),
    path('beans/<int:bean_id>', BeanDetailView.as_view()),
    path('recipes', RecipeListCreateView.as_view()),
    path('recipes/<int:recipe_id>', RecipeDetailView.as_view()),
    path('recipes/<int:recipe_id>/reviews', RecipeReviewView.as_view()),
    path('users/<int:user_id>/favourites', UserFavouriteView.as_view()),
    path('users/<int:user_id>/favourites/<int:recipe_id>', UserFavouriteDetailView.as_view()),
    path('users/<int:user_id>/preferences', UserPreferencesView.as_view()),
    path('recommendations', RecommendationView.as_view()),
    path('brews/<int:brew_id>', BrewPartialUpdateView.as_view()),
]
