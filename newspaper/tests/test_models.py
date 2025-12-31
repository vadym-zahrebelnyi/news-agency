from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from newspaper.models import Topic, Article


class TopicModelTests(TestCase):
    def test_str_representation(self):
        topic = Topic.objects.create(name="Finance")
        self.assertEqual(str(topic), topic.name)


class RedactorModelTests(TestCase):
    def setUp(self):
        self.redactor = get_user_model().objects.create_user(
            username="test.user",
            password="password123",
            first_name="Test",
            last_name="User",
            years_of_experience=5,
        )

    def test_str_representation(self):
        expected_str = (
            f"{self.redactor.username} "
            f"({self.redactor.first_name} {self.redactor.last_name})"
        )
        self.assertEqual(str(self.redactor), expected_str)

    def test_get_absolute_url(self):
        expected_url = reverse(
            "newspaper:redactor-detail", kwargs={"pk": self.redactor.pk}
        )
        self.assertEqual(self.redactor.get_absolute_url(), expected_url)

    def test_years_of_experience_default(self):
        new_redactor = get_user_model().objects.create_user(
            username="new.user", password="password123"
        )
        self.assertEqual(new_redactor.years_of_experience, 0)

    def test_years_of_experience_max_value(self):
        redactor = get_user_model()(
            username="high.experience",
            password="password123",
            years_of_experience=51,
        )
        with self.assertRaisesMessage(
            ValidationError, "Ensure this value is less than or equal to 50."
        ):
            redactor.full_clean()


class ArticleModelTests(TestCase):
    def setUp(self):
        self.redactor = get_user_model().objects.create_user(
            username="author.user", password="password123"
        )
        self.topic1 = Topic.objects.create(name="Sports")
        self.topic2 = Topic.objects.create(name="World News")
        self.article = Article.objects.create(
            title="Breaking News: A Major Event Happened",
            content="Here are the details of the event.",
        )

    def test_str_representation(self):
        self.assertEqual(str(self.article), self.article.title)

    def test_add_topics_to_article(self):
        self.article.topics.add(self.topic1, self.topic2)
        self.assertEqual(self.article.topics.count(), 2)
        self.assertIn(self.topic1, self.article.topics.all())
        self.assertIn(self.topic2, self.article.topics.all())

    def test_add_publishers_to_article(self):
        self.article.publishers.add(self.redactor)
        self.assertEqual(self.article.publishers.count(), 1)
        self.assertIn(self.redactor, self.article.publishers.all())
