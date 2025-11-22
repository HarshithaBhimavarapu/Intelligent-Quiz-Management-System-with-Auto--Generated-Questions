from django.contrib import admin
from .models import User, Profile, Category, Subcategory, Quiz, QuizAttempt

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Quiz)
admin.site.register(QuizAttempt)

