from django.test import TestCase
from django.db import IntegrityError
from .models import User, Bean, Recipe, Brew, Review, Favourite


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password',
        )
        self.assertEqual(user.username, 'testuser')
        self.assertIsNotNone(user.created_at)

    def test_username_unique(self):
        User.objects.create(username='alice', email='alice@example.com', password_hash='hash1')
        with self.assertRaises(IntegrityError):
            User.objects.create(username='alice', email='other@example.com', password_hash='hash2')

    def test_email_unique(self):
        User.objects.create(username='alice', email='alice@example.com', password_hash='hash1')
        with self.assertRaises(IntegrityError):
            User.objects.create(username='bob', email='alice@example.com', password_hash='hash2')


class BeanModelTest(TestCase):
    def test_create_bean(self):
        bean = Bean.objects.create(name='Ethiopian Yirgacheffe', origin='Ethiopia', roast_level='Light')
        self.assertEqual(bean.name, 'Ethiopian Yirgacheffe')
        self.assertIsNotNone(bean.created_at)


class RecipeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='chef', email='chef@example.com', password_hash='hash')
        self.bean = Bean.objects.create(name='Arabica')

    def test_create_recipe(self):
        recipe = Recipe.objects.create(user=self.user, bean=self.bean, method='Pour Over', is_public=True)
        self.assertEqual(recipe.user, self.user)
        self.assertTrue(recipe.is_public)

    def test_recipe_default_not_public(self):
        recipe = Recipe.objects.create(user=self.user)
        self.assertFalse(recipe.is_public)


class BrewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='brewer', email='brewer@example.com', password_hash='hash')

    def test_create_brew(self):
        brew = Brew.objects.create(user=self.user, rating=5)
        self.assertEqual(brew.user, self.user)
        self.assertIsNotNone(brew.brewed_at)


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='reviewer', email='reviewer@example.com', password_hash='hash')
        owner = User.objects.create(username='owner', email='owner@example.com', password_hash='hash')
        self.recipe = Recipe.objects.create(user=owner)

    def test_create_review(self):
        review = Review.objects.create(reviewer=self.user, recipe=self.recipe, rating=4)
        self.assertEqual(review.rating, 4)

    def test_unique_reviewer_recipe(self):
        Review.objects.create(reviewer=self.user, recipe=self.recipe, rating=4)
        with self.assertRaises(IntegrityError):
            Review.objects.create(reviewer=self.user, recipe=self.recipe, rating=5)


class FavouriteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='fav_user', email='fav@example.com', password_hash='hash')
        owner = User.objects.create(username='owner2', email='owner2@example.com', password_hash='hash')
        self.recipe = Recipe.objects.create(user=owner)

    def test_create_favourite(self):
        fav = Favourite.objects.create(user=self.user, recipe=self.recipe)
        self.assertEqual(fav.user, self.user)

    def test_unique_user_recipe(self):
        Favourite.objects.create(user=self.user, recipe=self.recipe)
        with self.assertRaises(IntegrityError):
            Favourite.objects.create(user=self.user, recipe=self.recipe)
