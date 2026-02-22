from rest_framework import viewsets
from .models import User, Bean, Recipe, Brew, Review, Favourite
from .serializers import (
    UserSerializer, BeanSerializer, RecipeSerializer,
    BrewSerializer, ReviewSerializer, FavouriteSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class BeanViewSet(viewsets.ModelViewSet):
    queryset = Bean.objects.all()
    serializer_class = BeanSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class BrewViewSet(viewsets.ModelViewSet):
    queryset = Brew.objects.all()
    serializer_class = BrewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class FavouriteViewSet(viewsets.ModelViewSet):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
