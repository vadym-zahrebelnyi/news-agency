from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Topic, Article

Redactor = get_user_model()

@admin.register(Redactor)
class RedactorAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("years_of_experience",)
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("years_of_experience",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "years_of_experience",
                )
            }
        ),
    )

@admin.register(Article)
class NewspaperAdmin(admin.ModelAdmin):
    list_display = ("title", "published_date")
    search_fields = ("title",)
    list_filter = ("topics", "published_date")
    filter_horizontal = ("topics", "publishers")

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
