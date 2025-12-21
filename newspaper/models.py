from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Index

class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "topic"
        verbose_name_plural = "topics"
        ordering = ["name"]
        indexes = [
            Index(fields=["name"], name="topic_name_idx"),
        ]

    def __str__(self):
        return self.name


class Redactor(AbstractUser):
    years_of_experience = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "redactor"
        verbose_name_plural = "redactors"

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class Article(models.Model):
    title = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    topics = models.ManyToManyField(Topic, related_name="articles")
    publishers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="articles"
    )

    class Meta:
        ordering = ["-published_date"]
        indexes = [
            Index(fields=["title"], name="newspaper_title_idx"),
            Index(fields=["published_date"], name="newspaper_pub_date_idx"),
        ]

    def __str__(self):
        return self.title