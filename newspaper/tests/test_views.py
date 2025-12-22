from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from newspaper.models import Topic, Article

Redactor = get_user_model()


class GeneralAccessTests(TestCase):
    def test_login_required_for_all_lists(self):
        """
        Tests that all main list pages redirect to the login page
        when the user is not authenticated.
        """
        urls = [
            reverse("newspaper:topic-list"),
            reverse("newspaper:article-list"),
            reverse("newspaper:redactor-list"),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_index_view_is_accessible(self):
        """Tests that the index page is accessible without logging in."""
        response = self.client.get(reverse("newspaper:index"))
        self.assertEqual(response.status_code, 200)


class AuthenticatedViewTests(TestCase):
    def setUp(self):
        self.user = Redactor.objects.create_user(
            username="test.user",
            password="password123",
            years_of_experience=5
        )
        self.client.force_login(self.user)
        self.topic = Topic.objects.create(name="Technology")
        self.article = Article.objects.create(title="Test Article", content="Test Content")
        self.article.publishers.add(self.user)

    def test_topic_list_view_search(self):
        """Tests that searching in the topic list filters correctly."""
        response = self.client.get(reverse("newspaper:topic-list") + "?name=Tech")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.topic.name)

    def test_article_list_view_search(self):
        """Tests that searching in the article list filters correctly."""
        response = self.client.get(reverse("newspaper:article-list") + "?title=Test")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)

    def test_redactor_detail_view(self):
        """Tests the redactor detail view displays correct user information."""
        response = self.client.get(reverse("newspaper:redactor-detail", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, str(self.user.years_of_experience))

    def test_user_can_delete_own_account(self):
        """Tests that a user can delete their own account."""
        response = self.client.post(reverse("newspaper:redactor-delete", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("newspaper:redactor-list"))
        self.assertFalse(Redactor.objects.filter(id=self.user.id).exists())


class ArticleViewTests(TestCase):
    def setUp(self):
        self.publisher_user = Redactor.objects.create_user(
            username="publisher.user",
            password="password123",
            years_of_experience=10
        )
        self.non_publisher_user = Redactor.objects.create_user(
            username="non.publisher",
            password="password123"
        )
        self.topic = Topic.objects.create(name="Science")
        self.article = Article.objects.create(title="Science Article", content="Content about science")
        self.article.publishers.add(self.publisher_user)

    def test_create_article_assigns_publisher(self):
        """Tests that the logged-in user is assigned as a publisher on creation."""
        self.client.force_login(self.publisher_user)
        form_data = {
            "title": "New Article by Publisher",
            "content": "Some fresh content",
            "topics": [self.topic.id]
        }
        response = self.client.post(reverse("newspaper:article-create"), data=form_data)
        self.assertRedirects(response, reverse("newspaper:article-list"))
        new_article = Article.objects.get(title="New Article by Publisher")
        self.assertIn(self.publisher_user, new_article.publishers.all())

    def test_publisher_can_update_article(self):
        """Tests that a user listed as a publisher can update the article."""
        self.client.force_login(self.publisher_user)
        updated_content = "This content has been updated."
        form_data = {
            "title": self.article.title,
            "content": updated_content,
            "topics": [self.topic.id]
        }
        response = self.client.post(
            reverse("newspaper:article-update", kwargs={"pk": self.article.id}),
            data=form_data
        )
        self.assertRedirects(response, reverse("newspaper:article-list"))
        self.article.refresh_from_db()
        self.assertEqual(self.article.content, updated_content)

    def test_non_publisher_cannot_update_article(self):
        """Tests that a user NOT listed as a publisher gets a 403 Forbidden on update."""
        self.client.force_login(self.non_publisher_user)
        form_data = {"title": self.article.title, "content": "Attempted update"}
        response = self.client.post(
            reverse("newspaper:article-update", kwargs={"pk": self.article.id}),
            data=form_data
        )
        self.assertEqual(response.status_code, 403)

    def test_publisher_can_delete_article(self):
        """Tests that a user listed as a publisher can delete the article."""
        self.client.force_login(self.publisher_user)
        response = self.client.post(reverse("newspaper:article-delete", kwargs={"pk": self.article.id}))
        self.assertRedirects(response, reverse("newspaper:article-list"))
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_non_publisher_cannot_delete_article(self):
        """Tests that a user NOT listed as a publisher gets a 403 Forbidden on delete."""
        self.client.force_login(self.non_publisher_user)
        response = self.client.post(reverse("newspaper:article-delete", kwargs={"pk": self.article.id}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Article.objects.filter(id=self.article.id).exists())
