from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class Bean(models.Model):
    name = models.CharField(max_length=255)
    origin = models.CharField(max_length=255, blank=True, null=True)
    roast_level = models.CharField(max_length=50, blank=True, null=True)
    flavour_tags = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'beans'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    bean = models.ForeignKey(Bean, on_delete=models.SET_NULL, null=True, blank=True, related_name='recipes')
    method = models.CharField(max_length=100, blank=True, null=True)
    water_temp = models.IntegerField(blank=True, null=True)
    grind_size = models.CharField(max_length=50, blank=True, null=True)
    brew_time = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recipes'

    def __str__(self):
        return f"Recipe {self.id} by {self.user}"


class Brew(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='brews')
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True, related_name='brews')
    actual_temp = models.IntegerField(blank=True, null=True)
    actual_time = models.IntegerField(blank=True, null=True)
    rating = models.IntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    notes = models.TextField(blank=True, null=True)
    brewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'brews'

    def __str__(self):
        return f"Brew {self.id} by {self.user}"


class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        constraints = [
            models.UniqueConstraint(fields=['reviewer', 'recipe'], name='uq_reviews_reviewer_recipe')
        ]

    def __str__(self):
        return f"Review {self.id} by {self.reviewer} on Recipe {self.recipe_id}"


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favourited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favourites'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='pk_favourites_user_recipe')
        ]

    def __str__(self):
        return f"Favourite: User {self.user_id} -> Recipe {self.recipe_id}"
