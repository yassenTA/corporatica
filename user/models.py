from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
class TimestampedModel(models.Model):
    """
    Abstract model to contain information about creation/update time.

    :created_at: date and time of record creation.
    :updated_at: date and time of any update happends for the record.
    """

    created_at = models.DateTimeField(
        verbose_name="Created Date/Time", auto_now_add=True
    )
    updated_at = models.DateTimeField(verbose_name="Update Date/Time", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at", "-updated_at"]


class User(AbstractUser):
    username = models.CharField(
        _("username"),
        max_length=150,
        null=True,
        blank=True,
        unique=True,
    )

    USERNAME_FIELD = "username"

    class Meta:
        ordering = ["-id"]
        verbose_name = _("User")
        verbose_name_plural = _("User")

    def __str__(self):
        return self.email
