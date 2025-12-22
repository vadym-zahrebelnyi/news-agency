from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin.user", password="password123"
        )
        self.client.force_login(self.admin_user)
        self.redactor = get_user_model().objects.create_user(
            username="test.redactor",
            password="password123",
            years_of_experience=10,
        )

    def test_redactor_years_of_experience_listed(self):
        """
        Tests that the 'years_of_experience' field is displayed on the redactor list page.
        """
        url = reverse("admin:newspaper_redactor_changelist")
        response = self.client.get(url)
        self.assertContains(response, str(self.redactor.years_of_experience))

    def test_redactor_detail_years_of_experience_listed(self):
        """
        Tests that the 'years_of_experience' field is displayed on the redactor detail/change page.
        """
        url = reverse("admin:newspaper_redactor_change", args=[self.redactor.id])
        response = self.client.get(url)
        self.assertContains(response, "years_of_experience")  # Check for the label
        self.assertContains(response, self.redactor.years_of_experience)  # Check for the value

    def test_redactor_create_years_of_experience_listed(self):
        """
        Tests that the 'years_of_experience' field is present on the redactor create page.
        """
        url = reverse("admin:newspaper_redactor_add")
        response = self.client.get(url)
        self.assertContains(response, "years_of_experience")
