import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Avg, Count
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import User, Bean, Recipe, Brew, Review, Favourite, UserToken
from .serializers import (
    UserSerializer, BeanSerializer, RecipeSerializer,
    BrewSerializer, ReviewSerializer, FavouriteSerializer,
)


def _get_auth_token(request):
    authorization = request.headers.get('Authorization', '')
    if not authorization.startswith('Bearer '):
        return None
    return authorization.replace('Bearer ', '', 1).strip()


def _get_authenticated_user(request):
    token = _get_auth_token(request)
    if not token:
        return None
    try:
        return UserToken.objects.select_related('user').get(token=token).user
    except UserToken.DoesNotExist:
        return None


@ensure_csrf_cookie
def frontend_home(request):
    return redirect('frontend-recipes')


@ensure_csrf_cookie
def frontend_auth(request):
    return render(request, 'coffee/auth.html', {'active_page': 'auth'})


@ensure_csrf_cookie
def frontend_register(request):
    return render(request, 'coffee/register.html', {'active_page': 'register'})


@ensure_csrf_cookie
def frontend_user_profile(request):
    return render(request, 'coffee/user_profile.html', {'active_page': 'user'})


@ensure_csrf_cookie
def frontend_beans(request):
    return render(request, 'coffee/beans.html', {'active_page': 'beans'})


@ensure_csrf_cookie
def frontend_recipes(request):
    return render(request, 'coffee/recipes.html', {'active_page': 'recipes'})


@ensure_csrf_cookie
def frontend_recipe_detail(request, recipe_id):
    return render(request, 'coffee/recipe_detail.html', {'recipe_id': recipe_id, 'active_page': 'recipes'})


@ensure_csrf_cookie
def frontend_create_recipe(request):
    return render(request, 'coffee/create_recipe.html', {'active_page': 'create'})


@ensure_csrf_cookie
def frontend_log_brew(request):
    return render(request, 'coffee/log_brew.html', {'active_page': 'brew'})


@ensure_csrf_cookie
def frontend_analytics(request):
    return render(request, 'coffee/analytics.html', {'active_page': 'analytics'})


@api_view(['POST'])
def auth_register(request):
    """
    Register a new user account and return a bearer token.

    Request body:
    - username
    - email
    - password
    """
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    if not username or not email or not password:
        return Response({'detail': 'username, email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 6:
        return Response({'detail': 'Password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'detail': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create(username=username, email=email, password_hash=make_password(password))
    token_value = secrets.token_hex(24)
    UserToken.objects.create(user=user, token=token_value)

    return Response(
        {
            'token': token_value,
            'user': UserSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
def auth_login(request):
    """
    Authenticate with username/email and password, then return a bearer token.

    Supports legacy plaintext password hashes and upgrades them to Django hashes
    after a successful login.
    """
    username_or_email = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    if not username_or_email or not password:
        return Response({'detail': 'username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(username=username_or_email).first() or User.objects.filter(email=username_or_email).first()
    password_ok = False
    if user:
        password_ok = check_password(password, user.password_hash)
        if not password_ok and user.password_hash == password:
            password_ok = True
            user.password_hash = make_password(password)
            user.save(update_fields=['password_hash'])

    if not user or not password_ok:
        return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    token_value = secrets.token_hex(24)
    UserToken.objects.update_or_create(user=user, defaults={'token': token_value})
    return Response({'token': token_value, 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def auth_me(request):
    """
    Return the currently authenticated user based on bearer token.
    """
    user = _get_authenticated_user(request)
    if not user:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'user': UserSerializer(user).data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def auth_logout(request):
    """
    Invalidate the current bearer token.
    """
    token = _get_auth_token(request)
    if not token:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
    UserToken.objects.filter(token=token).delete()
    return Response({'detail': 'Logged out.'}, status=status.HTTP_200_OK)


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

    def get_queryset(self):
        queryset = Bean.objects.all().order_by('name')
        origin = self.request.query_params.get('origin')
        roast_level = self.request.query_params.get('roast_level')

        if origin:
            queryset = queryset.filter(origin__iexact=origin)
        if roast_level:
            queryset = queryset.filter(roast_level__iexact=roast_level)
        return queryset


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

    def get_queryset(self):
        queryset = Recipe.objects.select_related('bean', 'user').all().order_by('-created_at')
        is_public = self.request.query_params.get('is_public')
        bean_id = self.request.query_params.get('bean')

        if is_public is not None:
            is_public_value = is_public.lower() in ['1', 'true', 'yes']
            queryset = queryset.filter(is_public=is_public_value)
        if bean_id:
            queryset = queryset.filter(bean_id=bean_id)
        return queryset

    def create(self, request, *args, **kwargs):
        user = _get_authenticated_user(request)
        if not user:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        data['user'] = user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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

    def get_queryset(self):
        queryset = Brew.objects.select_related('recipe', 'user').all().order_by('-brewed_at')
        recipe_id = self.request.query_params.get('recipe')
        user_id = self.request.query_params.get('user')
        auth_user = _get_authenticated_user(self.request)

        if recipe_id:
            queryset = queryset.filter(recipe_id=recipe_id)
        if user_id:
            if not auth_user or str(auth_user.id) != str(user_id):
                return queryset.none()
            queryset = queryset.filter(user_id=user_id)
        return queryset

    def create(self, request, *args, **kwargs):
        user = _get_authenticated_user(request)
        if not user:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        data['user'] = user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        user = _get_authenticated_user(request)
        if not user:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        instance = self.get_object()
        if instance.user_id != user.id:
            return Response({'detail': 'You can only modify your own brew logs.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['user'] = user.id
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        user = _get_authenticated_user(request)
        if not user:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        instance = self.get_object()
        if instance.user_id != user.id:
            return Response({'detail': 'You can only modify your own brew logs.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['user'] = user.id
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = _get_authenticated_user(request)
        if not user:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        instance = self.get_object()
        if instance.user_id != user.id:
            return Response({'detail': 'You can only delete your own brew logs.'}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


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

    def get_queryset(self):
        queryset = Review.objects.select_related('recipe', 'reviewer').all().order_by('-created_at')
        recipe_id = self.request.query_params.get('recipe')
        if recipe_id:
            queryset = queryset.filter(recipe_id=recipe_id)
        return queryset

    def create(self, request, *args, **kwargs):
        user = _get_authenticated_user(request)
        if not user:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        data['reviewer'] = user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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

    def get_queryset(self):
        queryset = Favourite.objects.select_related('recipe', 'user').all().order_by('-created_at')
        user_id = self.request.query_params.get('user')
        recipe_id = self.request.query_params.get('recipe')

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if recipe_id:
            queryset = queryset.filter(recipe_id=recipe_id)
        return queryset

    def create(self, request, *args, **kwargs):
        user = _get_authenticated_user(request)
        if not user:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        data['user'] = user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        user = _get_authenticated_user(request)
        if not user:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        instance = self.get_object()
        if instance.user_id != user.id:
            return Response({'detail': 'You can only remove your own favourites.'}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def analytics_summary(request):
    """
    Return aggregate analytics for public coffee activity.

    Includes:
    - popular brew methods
    - average ratings by bean origin
    - most favourited public recipes
    """
    popular_methods = (
        Recipe.objects.filter(is_public=True)
        .exclude(method__isnull=True)
        .exclude(method__exact='')
        .values('method')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )

    average_ratings_by_origin = (
        Review.objects.filter(recipe__bean__origin__isnull=False)
        .exclude(recipe__bean__origin__exact='')
        .values('recipe__bean__origin')
        .annotate(avg_rating=Avg('rating'), total_reviews=Count('id'))
        .order_by('-avg_rating', '-total_reviews')[:8]
    )

    most_favourited = (
        Recipe.objects.filter(is_public=True)
        .annotate(favourites_count=Coalesce(Count('favourited_by'), 0), review_avg=Avg('reviews__rating'))
        .order_by('-favourites_count', '-review_avg')[:8]
    )

    return Response(
        {
            'popular_methods': list(popular_methods),
            'average_ratings_by_origin': [
                {
                    'origin': entry['recipe__bean__origin'],
                    'avg_rating': round(entry['avg_rating'], 2) if entry['avg_rating'] is not None else None,
                    'total_reviews': entry['total_reviews'],
                }
                for entry in average_ratings_by_origin
            ],
            'most_favourited_recipes': [
                {
                    'id': recipe.id,
                    'method': recipe.method,
                    'bean_id': recipe.bean_id,
                    'favourites_count': recipe.favourites_count,
                    'average_rating': round(recipe.review_avg, 2) if recipe.review_avg is not None else None,
                }
                for recipe in most_favourited
            ],
        }
    )
