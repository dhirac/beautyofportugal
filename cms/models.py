from django.db import models
from lib.models import BaseModel
from django.utils.text import slugify 
from django.utils import timezone
import humanize
from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.conf import settings
import uuid
from django.core.files.storage import default_storage


class Category(BaseModel):
 
    title=models.CharField(max_length=150)
    description = models.TextField(max_length=300)
    thumbnail = models.ImageField(null=True, blank=True, upload_to="images/")
    slug = models.SlugField(unique=True,blank=True, null=True)
    DisplayFields = ['title','description','thumbnail']
    SearchableFields = ['title','description']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "categories"


class Post(BaseModel):
   
    title=models.CharField(max_length=150)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="post")
    slug = models.SlugField(unique=True,blank=True, null=True)
    banner = models.ImageField(null=True,blank=True,upload_to="images/" )
    is_published = models.BooleanField(default=True)
    is_feature = models.BooleanField(default=False)
    DisplayFields = ['title','category','banner','is_published','is_feature']
    SearchableFields = ['title','Category']
    FilterFields = ['category','is_feature','is_published']
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    @property 
    def time_diff(self):
        current_time = timezone.now()
        time_difference = current_time - self.created_at
        return  humanize.naturaltime(time_difference)
    
    class Meta:
        verbose_name_plural = "posts"


class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs")
    title = models.CharField(max_length=150)
    description = models.TextField()
    slug = models.SlugField(unique=True, blank=True, null=True)
    banner = models.ImageField(null=True, blank=True, upload_to="images/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug or self.slug.strip() == "":
            # Create slug from title + short UUID
            unique_id = str(uuid.uuid4())[:8]  # 8-char unique string
            self.slug = f"{slugify(self.title)}-{unique_id}"
        super().save(*args, **kwargs)



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  # Avatar field for file upload

    def __str__(self):
        return self.user.username
    

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    original_image = models.ImageField(upload_to='photos/original/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='photos/thumbnails/', null=True, blank=True)
    watermarked_image = models.ImageField(upload_to='photos/watermarked/', null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.TextField()
    slug = models.SlugField(unique=True, max_length=400)
    total_views = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_unique_filename(self, filename):
        unique_id = uuid.uuid4()
        base, extension = os.path.splitext(filename)
        return f"{base}_{unique_id}{extension}"

    def save(self, *args, **kwargs):
        # Ensure unique filename
        if not self.pk and self.original_image:
            self.original_image.name = self.get_unique_filename(self.original_image.name)

        # Ensure unique slug
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            while Photo.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            self.slug = slug

        # Save first to get PK
        super().save(*args, **kwargs)

        # Generate thumbnail and watermark if not exist
        if self.original_image and (not self.thumbnail or not self.watermarked_image):
            self.generate_thumbnail_and_watermark()

    def generate_thumbnail_and_watermark(self):
        """Generate a thumbnail and watermarked version."""
        original_image_path = self.original_image.path

        with Image.open(original_image_path) as img:
            # Convert RGBA/P images to RGB for JPEG
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Thumbnail generation
            width, height = img.size
            aspect_ratio = width / height
            thumbnail_max_size = 900
            if aspect_ratio > 1:
                thumbnail_size = (thumbnail_max_size, int(thumbnail_max_size / aspect_ratio))
            else:
                thumbnail_size = (int(thumbnail_max_size * aspect_ratio), thumbnail_max_size)
            img.thumbnail(thumbnail_size)

            # Save thumbnail
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=95)
            thumb_file = ContentFile(thumb_io.getvalue(), 'thumbnail_' + os.path.basename(original_image_path))
            self.thumbnail.save(thumb_file.name, thumb_file, save=False)

            # Watermark
            watermark_image = img.copy()
            draw = ImageDraw.Draw(watermark_image)
            font = ImageFont.load_default()
            watermark_text = "BeautyOfPortugal"
            text_width, text_height = draw.textbbox((0, 0), watermark_text, font=font)[2:4]
            x = watermark_image.width - text_width - 10
            y = watermark_image.height - text_height - 10
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255))

            # Save watermarked image
            water_io = BytesIO()
            watermark_image.save(water_io, format='JPEG', quality=95)
            water_file = ContentFile(water_io.getvalue(), 'watermarked_' + os.path.basename(original_image_path))
            self.watermarked_image.save(water_file.name, water_file, save=False)

        # Save once after generating files
        super().save(update_fields=['thumbnail', 'watermarked_image'])


    def remove_old_files(self, old_instance):
        """Remove old files from storage."""
        if old_instance.original_image and old_instance.original_image != self.original_image:
            if default_storage.exists(old_instance.original_image.path):
                default_storage.delete(old_instance.original_image.path)
        
        if old_instance.thumbnail and old_instance.thumbnail != self.thumbnail:
            if default_storage.exists(old_instance.thumbnail.path):
                default_storage.delete(old_instance.thumbnail.path)
        
        if old_instance.watermarked_image and old_instance.watermarked_image != self.watermarked_image:
            if default_storage.exists(old_instance.watermarked_image.path):
                default_storage.delete(old_instance.watermarked_image.path)

    def delete(self, *args, **kwargs):
        # Delete images from storage before deleting the model
        if self.original_image and default_storage.exists(self.original_image.path):
            default_storage.delete(self.original_image.path)
        
        if self.thumbnail and default_storage.exists(self.thumbnail.path):
            default_storage.delete(self.thumbnail.path)
        
        if self.watermarked_image and default_storage.exists(self.watermarked_image.path):
            default_storage.delete(self.watermarked_image.path)

        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    photo = models.ForeignKey(Photo, related_name='comments', on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.photo.title}"
    

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='event_banners/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.event.title}"