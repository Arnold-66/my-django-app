from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from .models import Profile

@receiver(post_save, sender=Profile)
def resize_image(sender, instance, created, **kwargs):
    if created:
        img = Image.open(instance.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(instance.image.path)
