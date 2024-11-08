from django.db import models
from user.models import TimestampedModel


class DataSet(TimestampedModel):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/")

    def __str__(self):
        return self.name
