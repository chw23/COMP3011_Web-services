from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Bean, Recipe, Brew, Review, Favourite


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'created_at']

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        validated_data['password_hash'] = make_password(raw_password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        raw_password = validated_data.pop('password', None)
        if raw_password:
            instance.password_hash = make_password(raw_password)
        return super().update(instance, validated_data)


class BeanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bean
        fields = ['id', 'name', 'origin', 'roast_level', 'flavour_tags', 'created_at']


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id', 'user', 'bean', 'method', 'water_temp',
            'grind_size', 'brew_time', 'description', 'is_public', 'created_at'
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
