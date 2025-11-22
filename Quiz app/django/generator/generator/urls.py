"""
URL configuration for generator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib.auth import views as auth_views
from django.contrib import admin
from quiz_app import views

from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('register/', views.register, name='register'), 
    path('', views.register, name='home'),
    path('admin/', admin.site.register),
    path("login/", views.login_view, name="login"),
    path("home/", views.home_view, name="home"),
    
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("logout/", views.logout_view, name="logout"),
    path('logout/', views.logout_view, name="logout"),
    path('categories/', views.quiz_categories, name="quiz_categories"),
    path('profile/', views.profile_view, name='profile'),
    path("categories/", views.categories, name="quiz_categories"),
    path("categories/<int:category_id>/", views.subcategories, name="subcategory_page"),
    path('categories/<int:category_id>/subcategories/', views.subcategories, name='subcategories'),
    path('categories/<int:category_id>/subcategories/<int:subcategory_id>/quiz/<str:difficulty>/', 
         views.generate_quiz, name='generate_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('about-us/', views.about_us, name='about_us'),
    path('subcategories/<int:subcategory_id>/quiz/submit/', views.submit_quiz, name='submit_quiz'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path("dashboard-data/", views.dashboard_data, name="dashboard_data"), 
    path('submit_quiz/', views.submit_quiz, name='submit_quiz'),
    path('subcategories/<int:subcategory_id>/quiz/', views.quiz_list, name='quiz_list'),
    path('subcategories/<int:subcategory_id>/quiz/submit/', views.submit_quiz, name='submit_quiz'),
    path('resume-quiz/<int:attempt_id>/', views.resume_quiz_view, name='resume_quiz'),
    path('view-attempt/<int:attempt_id>/', views.view_attempt_view, name='view_attempt'),
    path('resume-attempt/<int:attempt_id>/', views.resume_quiz_view, name='resume_quiz'),
    path('submit-resumed-quiz/<int:attempt_id>/', views.submit_resumed_quiz, name='submit_resumed_quiz'),
    path(
    "categories/<int:category_id>/subcategories/<int:subcategory_id>/quiz/<str:difficulty>/<int:question_count>/",
    views.generate_quiz,
    name="generate_quiz"),
     path('get_hint/<int:question_id>/', views.get_hint, name='get_hint'),
      
]
    
  

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
