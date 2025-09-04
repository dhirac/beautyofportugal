"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
   path('', views.landing, name='landing'),
   path('gallery/<slug:category_slug>/', views.gallery, name='gallery'),
   path('photo/gallery/<slug:slug>/', views.photo_detail, name='photo_detail'),
   path('photographers/', views.photographers, name='photographers'),
   path('aboutus/', views.about_us, name='aboutus'),
   path('blog/', views.blog_list, name='blog'),
   path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
   path('event/<int:id>/', views.event_detail, name='event_detail'),
   path('contact/', views.contact, name='contact'),

]
