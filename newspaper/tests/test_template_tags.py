from django.test import TestCase, RequestFactory
from urllib.parse import parse_qs

from newspaper.templatetags.query_transform import query_transform


class TemplateTagsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_query_transform_add_parameter(self):
        """Tests adding a new parameter to an existing query."""
        request = self.factory.get("/test-path?search=test")
        result = query_transform(request, page=2)
        self.assertEqual(parse_qs(result), {"search": ["test"], "page": ["2"]})

    def test_query_transform_update_parameter(self):
        """Tests updating an existing parameter in the query."""
        request = self.factory.get("/test-path?page=1&search=car")
        result = query_transform(request, page=3)
        self.assertEqual(parse_qs(result), {"search": ["car"], "page": ["3"]})

    def test_query_transform_remove_parameter(self):
        """Tests removing a parameter from the query."""
        request = self.factory.get("/test-path?page=2&search=car")
        result = query_transform(request, page=None)
        self.assertEqual(parse_qs(result), {"search": ["car"]})

    def test_query_transform_multiple_changes(self):
        """Tests multiple modifications (add, update, remove) at once."""
        request = self.factory.get("/test-path?page=1&order=asc")
        result = query_transform(request, page=2, order=None, new="val")
        self.assertEqual(parse_qs(result), {"page": ["2"], "new": ["val"]})

    def test_query_transform_no_initial_params(self):
        """Tests adding a parameter when the initial query is empty."""
        request = self.factory.get("/test-path")
        result = query_transform(request, page=1)
        self.assertEqual(parse_qs(result), {"page": ["1"]})