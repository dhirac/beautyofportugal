# forms.py
from django import forms
from .models import Blog, EventRegistration, Profile
from .models import Photo, Category
from tinymce.widgets import TinyMCE
from django.core.exceptions import ValidationError
import os
from django.db import models



class ProfileUpdateForm(forms.ModelForm):
  
    email = forms.EmailField(disabled=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    class Meta:
        model = Profile
        fields = ['full_name', 'avatar']  # Fields for updating full_name and avatar
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
           
            'avatar': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email  # Populate email from User model


class PhotoUploadForm(forms.ModelForm):
    metadata = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))  # TinyMCE for metadata

    class Meta:
        model = Photo
        fields = ['title', 'description', 'original_image', 'category', 'metadata']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter photo title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter photo description'}),
            'original_image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'metadata': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Enter photo description'}),
        }

    def clean_original_image(self):
        original_image = self.cleaned_data.get('original_image')

        # Check if an image is uploaded
        if not original_image:
            raise ValidationError("No image was uploaded!")

        # Check the file extension (allow only JPEG and PNG)
        valid_extensions = ['.jpg', '.jpeg', '.png']
        ext = os.path.splitext(original_image.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError("Invalid file format! Only JPEG and PNG are allowed.")

        # Check the file size (e.g., limit to 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if original_image.size > max_size:
            raise ValidationError(f"The file is too large! Maximum file size allowed is 5MB.")

        return original_image


class PhotoEditForm(forms.ModelForm):
    metadata = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))  # TinyMCE for metadata

    class Meta:
        model = Photo
        fields = ['title', 'description', 'category','metadata']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter photo title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter photo description'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'metadata': forms.Textarea(attrs={'class': 'form-control'}),
        }


class BlogForm(forms.ModelForm):
    description = models.TextField()
    class Meta:
        model = Blog
        fields = ['title', 'description', 'banner']



class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['name', 'email', 'phone']
