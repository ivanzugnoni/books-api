import uuid

from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel


class UUIDModelMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, UUIDModelMixin):
    class Meta:
        abstract = True


class Author(BaseModel):
    name = models.CharField(max_length=1500)
    biography = models.TextField(blank=True)
    birthday = models.DateField(blank=True, null=True)

    @property
    def age(self):
        return int((timezone.now().date() - self.birthday).days / 365)

    def __str__(self):
        return f"{self.name}"


class Collaborator(BaseModel):
    name = models.CharField(max_length=1500)

    def __str__(self):
        return f"{self.name}"


class Book(BaseModel):
    author = models.ForeignKey(
        "books.Author", on_delete=models.CASCADE, related_name="books"
    )
    collaborators = models.ManyToManyField(
        "books.Collaborator", related_name="books", blank=True
    )
    name = models.CharField(max_length=1500)
    publish_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
