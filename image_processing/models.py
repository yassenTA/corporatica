# image_processing/models.py
from django.db import models
from user.models import TimestampedModel


class UploadedImage(TimestampedModel):
    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return f"Image {self.id}: {self.image.name}"
