from django.test import TestCase
from newspaper.forms import (
    RedactorCreationForm,
    RedactorUpdateForm,
    ArticleForm,
    TopicSearchForm,
    ArticleSearchForm,
)
from newspaper.models import Topic


class SearchFormsTests(TestCase):
    def test_topic_search_form(self):
        form_empty = TopicSearchForm(data={})
        self.assertTrue(form_empty.is_valid())
        self.assertEqual(form_empty.cleaned_data, {"name": ""})

        form_with_data = TopicSearchForm(data={"name": "Test"})
        self.assertTrue(form_with_data.is_valid())
        self.assertEqual(form_with_data.cleaned_data, {"name": "Test"})

    def test_article_search_form(self):
        form_empty = ArticleSearchForm(data={})
        self.assertTrue(form_empty.is_valid())
        self.assertEqual(form_empty.cleaned_data, {"title": ""})

        form_with_data = ArticleSearchForm(data={"title": "Test"})
        self.assertTrue(form_with_data.is_valid())
        self.assertEqual(form_with_data.cleaned_data, {"title": "Test"})


class RedactorFormsTests(TestCase):
    def test_redactor_creation_form_valid_experience(self):
        form_data = {
            "username": "test.user",
            "password1": "S0meC0mplexP@ssword!",
            "password2": "S0meC0mplexP@ssword!",
            "years_of_experience": 10,
        }
        form = RedactorCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_redactor_creation_form_negative_experience_invalid(self):
        form_data = {
            "username": "test.user",
            "password1": "S0meC0mplexP@ssword!",
            "password2": "S0meC0mplexP@ssword!",
            "years_of_experience": -5,
        }
        form = RedactorCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("years_of_experience", form.errors)
        self.assertEqual(
            form.errors["years_of_experience"][0],
            "Ensure this value is greater than or equal to 0.",
        )

    def test_redactor_update_form_valid(self):
        form_data = {
            "username": "test_user",
            "years_of_experience": 20,
            "first_name": "Test",
            "last_name": "User",
        }
        form = RedactorUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())


class ArticleFormTests(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name="Test Topic")

    def test_article_form_valid(self):
        form_data = {
            "title": "A Valid Title",
            "content": "Some valid content.",
            "topics": [self.topic.id],
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_article_form_missing_title_invalid(self):
        form_data = {
            "content": "Content without a title.",
            "topics": [self.topic.id],
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
