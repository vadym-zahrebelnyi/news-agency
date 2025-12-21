from django.urls import path
from .views import (
    IndexView,

    TopicListView,
    TopicCreateView,
    TopicUpdateView,
    TopicDeleteView,

    RedactorListView,
    RedactorDetailView,
)


urlpatterns = [
    path("", IndexView.as_view(), name="index"),

    path("topics/", TopicListView.as_view(), name="topic-list"),
    path("topics/create/", TopicCreateView.as_view(), name="topic-create"),
    path("topics/<int:pk>/update/", TopicUpdateView.as_view(), name="topic-update"),
    path("topics/<int:pk>/delete/", TopicDeleteView.as_view(), name="topic-delete"),

    path("redactors/", RedactorListView.as_view(), name="redactor-list"),
    path("redactors/<int:pk>/", RedactorDetailView.as_view(), name="redactor-detail"),
]

app_name = "newspaper"