from rest_framework import serializers
from .models import User, Bean, Recipe, Brew, Review, Favourite


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password_hash', 'created_at']
        extra_kwargs = {'password_hash': {'write_only': True}}


class BeanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bean
        fields = ['id', 'name', 'origin', 'roast_level', 'flavour_tags', 'created_at']


class RecipeSerializer(serializers.ModelSerializer):
    bean_name = serializers.CharField(source='bean.name', read_only=True)
    bean_origin = serializers.CharField(source='bean.origin', read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'user', 'bean', 'method', 'water_temp',
            'grind_size', 'brew_time', 'description', 'is_public', 'created_at',
            'bean_name', 'bean_origin'
        ]


class BrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brew
        fields = [
            'id', 'user', 'recipe', 'actual_temp', 'actual_time',
            'rating', 'notes', 'brewed_at'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'recipe', 'rating', 'comment', 'created_at']


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = ['id', 'user', 'recipe', 'created_at']
