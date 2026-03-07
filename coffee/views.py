from rest_framework import viewsets
from .models import User, Bean, Recipe, Brew, Review, Favourite
from .serializers import (
    UserSerializer, BeanSerializer, RecipeSerializer,
    BrewSerializer, ReviewSerializer, FavouriteSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    list:
    Return all users.

    retrieve:
    Return a single user by ID.

    create:
    Create a new user.

    update:
    Replace an existing user.

    partial_update:
    Update part of an existing user.

    destroy:
    Delete a user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class BeanViewSet(viewsets.ModelViewSet):
    """
    list:
    Return all beans.

    retrieve:
    Return a single bean by ID.

    create:
    Create a new bean.

    update:
    Replace an existing bean.

    partial_update:
    Update part of an existing bean.

    destroy:
    Delete a bean.
    """
    queryset = Bean.objects.all()
    serializer_class = BeanSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    list:
    Return all recipes.

    retrieve:
    Return a single recipe by ID.

    create:
    Create a new recipe.

    update:
    Replace an existing recipe.

    partial_update:
    Update part of an existing recipe.

    destroy:
    Delete a recipe.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class BrewViewSet(viewsets.ModelViewSet):
    """
    list:
    Return all brews.

    retrieve:
    Return a single brew by ID.

    create:
    Register a new brew.

    update:
    Replace an existing brew.

    partial_update:
    Update partial brew details (for example, rating or notes).

    destroy:
    Delete a brew.
    """
    queryset = Brew.objects.all()
    serializer_class = BrewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    list:
    Return all community reviews.

    retrieve:
    Return a single review by ID.

    create:
    Create a review for a recipe.

    update:
    Replace an existing review.

    partial_update:
    Update part of an existing review.

    destroy:
    Delete a review.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class FavouriteViewSet(viewsets.ModelViewSet):
    """
    list:
    Return all favourites.

    retrieve:
    Return a single favourite by ID.

    create:
    Mark a recipe as favourite.

    update:
    Replace an existing favourite relation.

    partial_update:
    Update part of an existing favourite relation.

    destroy:
    Remove a favourite.
    """
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
