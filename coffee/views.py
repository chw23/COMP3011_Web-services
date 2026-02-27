from django.contrib.auth.hashers import check_password
from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Bean, Recipe, Brew, Review, Favourite
from .serializers import (
    UserSerializer,
    BeanSerializer,
    RecipeSerializer,
    BrewSerializer,
    ReviewSerializer,
)


class UserCreateView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'detail': 'Both username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password_hash):
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        request.session['user_id'] = user.id
        request.session['username'] = user.username

        return Response(
            {
                'message': 'Login successful.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    def post(self, request):
        request.session.flush()
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)


class BeanListView(APIView):
    def get(self, request):
        queryset = Bean.objects.all()
        origin = request.query_params.get('origin')
        roast_level = request.query_params.get('roast_level')
        name = request.query_params.get('name')

        if origin:
            queryset = queryset.filter(origin__iexact=origin)
        if roast_level:
            queryset = queryset.filter(roast_level__iexact=roast_level)
        if name:
            queryset = queryset.filter(name__icontains=name)

        serializer = BeanSerializer(queryset, many=True)
        return Response(serializer.data)


class BeanDetailView(APIView):
    def get(self, request, bean_id):
        try:
            bean = Bean.objects.get(pk=bean_id)
        except Bean.DoesNotExist as exc:
            raise NotFound('Bean not found.') from exc

        serializer = BeanSerializer(bean)
        return Response(serializer.data)


class RecipeListCreateView(APIView):
    def get(self, request):
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RecipeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        return Response(RecipeSerializer(recipe).data, status=status.HTTP_201_CREATED)


class RecipeDetailView(APIView):
    def get_object(self, recipe_id):
        try:
            return Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist as exc:
            raise NotFound('Recipe not found.') from exc

    def put(self, request, recipe_id):
        recipe = self.get_object(recipe_id)
        serializer = RecipeSerializer(recipe, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, recipe_id):
        recipe = self.get_object(recipe_id)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeReviewView(APIView):
    def get_recipe(self, recipe_id):
        try:
            return Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist as exc:
            raise NotFound('Recipe not found.') from exc

    def get(self, request, recipe_id):
        recipe = self.get_recipe(recipe_id)
        reviews = Review.objects.filter(recipe=recipe).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, recipe_id):
        recipe = self.get_recipe(recipe_id)
        payload = request.data.copy()
        payload['recipe'] = recipe.id
        serializer = ReviewSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class UserFavouriteView(APIView):
    def post(self, request, user_id):
        recipe_id = request.data.get('recipe') or request.data.get('recipe_id')
        if not recipe_id:
            return Response(
                {'detail': 'recipe_id is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFound('User not found.') from exc

        try:
            recipe = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist as exc:
            raise NotFound('Recipe not found.') from exc

        favourite, created = Favourite.objects.get_or_create(user=user, recipe=recipe)
        response_data = {
            'id': favourite.id,
            'user': favourite.user_id,
            'recipe': favourite.recipe_id,
            'created_at': favourite.created_at,
        }
        return Response(
            response_data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class UserFavouriteDetailView(APIView):
    def delete(self, request, user_id, recipe_id):
        deleted_count, _ = Favourite.objects.filter(user_id=user_id, recipe_id=recipe_id).delete()
        if deleted_count == 0:
            return Response({'detail': 'Favourite not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPreferencesView(APIView):
    def get(self, request, user_id):
        if not User.objects.filter(pk=user_id).exists():
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        favourite_recipes = Recipe.objects.filter(favourited_by__user_id=user_id)
        reviewed_recipes = Recipe.objects.filter(reviews__reviewer_id=user_id)
        brewed_recipes = Recipe.objects.filter(brews__user_id=user_id)

        origins = list(
            Bean.objects.filter(recipes__in=(favourite_recipes | reviewed_recipes | brewed_recipes))
            .exclude(origin__isnull=True)
            .exclude(origin='')
            .values_list('origin', flat=True)
            .distinct()
        )
        methods = list(
            (favourite_recipes | reviewed_recipes | brewed_recipes)
            .exclude(method__isnull=True)
            .exclude(method='')
            .values_list('method', flat=True)
            .distinct()
        )

        avg_review_rating = (
            Review.objects.filter(reviewer_id=user_id).aggregate(value=Avg('rating'))['value']
        )
        avg_brew_rating = (
            Brew.objects.filter(user_id=user_id).aggregate(value=Avg('rating'))['value']
        )

        return Response(
            {
                'user_id': user_id,
                'preferred_origins': origins,
                'preferred_methods': methods,
                'avg_review_rating': avg_review_rating,
                'avg_brew_rating': avg_brew_rating,
                'favourite_count': Favourite.objects.filter(user_id=user_id).count(),
            }
        )


class RecommendationView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id') or request.session.get('user_id')
        base_queryset = Recipe.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating'),
        ).order_by('-avg_rating', '-review_count', '-created_at')

        if not user_id:
            serializer = RecipeSerializer(base_queryset[:10], many=True)
            return Response(serializer.data)

        preferred_origin_ids = Bean.objects.filter(
            recipes__favourited_by__user_id=user_id
        ).values_list('id', flat=True)

        personalized = base_queryset.filter(bean_id__in=preferred_origin_ids)
        if not personalized.exists():
            personalized = base_queryset

        serializer = RecipeSerializer(personalized[:10], many=True)
        return Response(serializer.data)


class BrewPartialUpdateView(APIView):
    def patch(self, request, brew_id):
        try:
            brew = Brew.objects.get(pk=brew_id)
        except Brew.DoesNotExist as exc:
            raise NotFound('Brew not found.') from exc

        serializer = BrewSerializer(brew, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
