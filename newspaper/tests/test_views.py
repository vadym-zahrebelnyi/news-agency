from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from newspaper.models import Topic, Article

Redactor = get_user_model()


class GeneralAccessTests(TestCase):
    def test_login_required_for_all_lists(self):
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
        response = self.client.get(reverse("newspaper:index"))
        self.assertEqual(response.status_code, 200)


class AuthenticatedViewTests(TestCase):
    def setUp(self):
        self.user = Redactor.objects.create_user(
            username="test.user",
            password="password123",
            years_of_experience=5,
        )
        self.client.force_login(self.user)
        self.topic = Topic.objects.create(name="Technology")
        self.article = Article.objects.create(
            title="Test Article", content="Test Content"
        )
        self.article.publishers.add(self.user)

    def test_topic_list_view_search(self):
        response = self.client.get(
            reverse("newspaper:topic-list") + "?name=Tech"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.topic.name)

    def test_topic_create_view(self):
        initial_count = Topic.objects.count()
        response = self.client.post(
            reverse("newspaper:topic-create"), data={"name": "New Topic"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("newspaper:topic-list"))
        self.assertEqual(Topic.objects.count(), initial_count + 1)
        self.assertTrue(Topic.objects.filter(name="New Topic").exists())

    def test_topic_update_view(self):
        response = self.client.post(
            reverse("newspaper:topic-update", kwargs={"pk": self.topic.id}),
            data={"name": "Updated Technology"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("newspaper:topic-list"))
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.name, "Updated Technology")

    def test_topic_delete_view(self):
        topic_to_delete = Topic.objects.create(name="Ephemeral Topic")
        initial_count = Topic.objects.count()
        response = self.client.post(
            reverse(
                "newspaper:topic-delete", kwargs={"pk": topic_to_delete.id}
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("newspaper:topic-list"))
        self.assertEqual(Topic.objects.count(), initial_count - 1)
        with self.assertRaises(Topic.DoesNotExist):
            Topic.objects.get(pk=topic_to_delete.id)

    def test_topic_list_view_pagination(self):
        for i in range(10):
            Topic.objects.create(name=f"Topic {i}")

        response = self.client.get(reverse("newspaper:topic-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "page")  # Check for pagination links

    def test_article_list_view_search(self):
        response = self.client.get(
            reverse("newspaper:article-list") + "?title=Test"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)

    def test_redactor_detail_view(self):
        response = self.client.get(
            reverse("newspaper:redactor-detail", kwargs={"pk": self.user.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, str(self.user.years_of_experience))

    def test_user_can_delete_own_account(self):
        response = self.client.post(
            reverse("newspaper:redactor-delete", kwargs={"pk": self.user.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("newspaper:redactor-list"))
        self.assertFalse(Redactor.objects.filter(id=self.user.id).exists())


class ArticleViewTests(TestCase):
    def setUp(self):
        self.publisher_user = Redactor.objects.create_user(
            username="publisher.user",
            password="password123",
            years_of_experience=10,
        )
        self.non_publisher_user = Redactor.objects.create_user(
            username="non.publisher", password="password123"
        )
        self.topic = Topic.objects.create(name="Science")
        self.article = Article.objects.create(
            title="Science Article", content="Content about science"
        )
        self.article.publishers.add(self.publisher_user)

    def test_article_detail_view(self):
        self.client.force_login(self.publisher_user)
        response = self.client.get(
            reverse(
                "newspaper:article-detail", kwargs={"pk": self.article.id}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        self.assertContains(response, self.article.content)

    def test_create_article_assigns_publisher(self):
        self.client.force_login(self.publisher_user)
        form_data = {
            "title": "New Article by Publisher",
            "content": "Some fresh content",
            "topics": [self.topic.id],
        }
        response = self.client.post(
            reverse("newspaper:article-create"), data=form_data
        )
        self.assertRedirects(response, reverse("newspaper:article-list"))
        new_article = Article.objects.get(title="New Article by Publisher")
        self.assertIn(self.publisher_user, new_article.publishers.all())

    def test_publisher_can_update_article(self):
        self.client.force_login(self.publisher_user)
        updated_content = "This content has been updated."
        form_data = {
            "title": self.article.title,
            "content": updated_content,
            "topics": [self.topic.id],
        }
        response = self.client.post(
            reverse(
                "newspaper:article-update", kwargs={"pk": self.article.id}
            ),
            data=form_data,
        )
        self.assertRedirects(response, reverse("newspaper:article-list"))
        self.article.refresh_from_db()
        self.assertEqual(self.article.content, updated_content)

    def test_non_publisher_cannot_update_article(self):
        self.client.force_login(self.non_publisher_user)
        form_data = {
            "title": self.article.title,
            "content": "Attempted update",
        }
        response = self.client.post(
            reverse(
                "newspaper:article-update", kwargs={"pk": self.article.id}
            ),
            data=form_data,
        )
        self.assertEqual(response.status_code, 403)

    def test_publisher_can_delete_article(self):
        self.client.force_login(self.publisher_user)
        response = self.client.post(
            reverse(
                "newspaper:article-delete", kwargs={"pk": self.article.id}
            )
        )
        self.assertRedirects(response, reverse("newspaper:article-list"))
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_non_publisher_cannot_delete_article(self):
        self.client.force_login(self.non_publisher_user)
        response = self.client.post(
            reverse(
                "newspaper:article-delete", kwargs={"pk": self.article.id}
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Article.objects.filter(id=self.article.id).exists())


class RedactorViewTests(TestCase):
    def setUp(self):
        self.user = Redactor.objects.create_user(
            username="regular.user",
            password="password123",
            years_of_experience=2,
        )
        self.other_user = Redactor.objects.create_user(
            username="other.user",
            password="password123",
            years_of_experience=5,
        )
        self.admin_user = Redactor.objects.create_superuser(
            username="admin.user", password="password123"
        )
        self.client.force_login(self.user)

    def test_redactor_create_view(self):
        self.client.logout()  # Ensure the client is not authenticated
        initial_count = Redactor.objects.count()
        form_data = {
            "username": "new.redactor",
            "password1": "S0meC0mplexP@ssword!",
            "password2": "S0meC0mplexP@ssword!",
            "years_of_experience": 1,
        }
        response = self.client.post(
            reverse("newspaper:redactor-create"), data=form_data
        )
        self.assertRedirects(
            response, reverse("newspaper:index")
        )  # Should redirect to index page after successful creation and login
        self.assertEqual(Redactor.objects.count(), initial_count + 1)

    def test_user_can_update_own_experience(self):
        form_data = {
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "years_of_experience": 3
        }
        response = self.client.post(
            reverse("newspaper:redactor-update", kwargs={"pk": self.user.id}),
            data=form_data,
        )
        self.assertRedirects(response, self.user.get_absolute_url())
        self.user.refresh_from_db()
        self.assertEqual(self.user.years_of_experience, 3)

    def test_user_cannot_update_other_user_experience(self):
        self.client.force_login(self.user)
        form_data = {"years_of_experience": 6}
        response = self.client.post(
            reverse(
                "newspaper:redactor-update", kwargs={"pk": self.other_user.id}
            ),
            data=form_data,
        )
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_admin_can_update_other_user_experience(self):
        self.client.force_login(self.admin_user)
        form_data = {
            "username": self.other_user.username,
            "first_name": self.other_user.first_name,
            "last_name": self.other_user.last_name,
            "years_of_experience": 7
        }
        response = self.client.post(
            reverse(
                "newspaper:redactor-update", kwargs={"pk": self.other_user.id}
            ),
            data=form_data,
        )
        self.assertRedirects(response, self.other_user.get_absolute_url())
        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.years_of_experience, 7)
