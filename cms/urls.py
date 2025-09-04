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
   
   path('dashboard/',views.dashboard,name="dashboard"),
   path('update_profile/', views.update_profile, name='update_profile'),
   path('upload_photo/', views.upload_photo, name='upload_photo'),
   path('edit_photo/<int:photo_id>/', views.edit_photo, name='edit_photo'),
   path('albums/', views.albums, name='albums'),
   path('album_photos/<slug:category_slug>/', views.album_photos, name='album_photos'),
   path('delete_photo/<int:photo_id>/', views.delete_photo, name='delete_photo'),
   path('upload-image-tinymce/', views.upload_image_tinymce, name='upload_image_tinymce'),



]
