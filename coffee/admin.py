from django.contrib import admin
from .models import User, Bean, Recipe, Brew, Review, Favourite

admin.site.register(User)
admin.site.register(Bean)
admin.site.register(Recipe)
admin.site.register(Brew)
admin.site.register(Review)
admin.site.register(Favourite)
