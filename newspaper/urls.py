from django.urls import path
from .views import (
    IndexView,
    TopicListView,
    TopicCreateView,
    TopicUpdateView,
    TopicDeleteView,
)


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("topics/", TopicListView.as_view(), name="topic-list"),
    path("topics/create/", TopicCreateView.as_view(), name="topic-create"),
    path("topics/<int:pk>/update/", TopicUpdateView.as_view(), name="topic-update"),
    path("topics/<int:pk>/delete/", TopicDeleteView.as_view(), name="topic-delete"),
]

app_name = "newspaper"