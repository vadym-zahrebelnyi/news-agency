import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from newspaper.models import Topic, Article

Redactor = get_user_model()
fake = Faker()

TEST_ADMIN = {
    "username": "admin",
    "password": "StrongAdminPassword456",
    "is_staff": True,
    "is_superuser": True,
}

TEST_AUTHORS = [
    {
        "username": "ivan_redactor",
        "password": "RedactorIvanPassword123",
        "years": 5,
    },
    {
        "username": "olga_news",
        "password": "RedactorOlgaPassword123",
        "years": 2,
    },
]


class Command(BaseCommand):
    help = "Seeds the database with initial data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")
        self._clear_db()

        admin = Redactor.objects.create_superuser(**TEST_ADMIN)
        self.stdout.write(f"Admin created: {admin.username}")

        authors = []
        for data in TEST_AUTHORS:
            author = Redactor.objects.create_user(
                username=data["username"],
                password=data["password"],
                years_of_experience=data["years"],
            )
            authors.append(author)

        for _ in range(20):
            extra_author = Redactor.objects.create_user(
                username=fake.user_name(),
                password="FakePassword123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                years_of_experience=random.randint(0, 30),
            )
            authors.append(extra_author)

        topics_list = [
            "Tech",
            "Politics",
            "Science",
            "Sport",
            "Health",
            "Nature",
            "Culture",
            "Literature",
            "Movies",
            "IT-Tech",
        ]
        topics = [Topic.objects.create(name=name) for name in topics_list]

        for _ in range(40):
            article = Article.objects.create(
                title=fake.sentence(nb_words=6),
                content="\n\n".join(fake.paragraphs(nb=5)),
            )
            article.topics.set(random.sample(topics, k=random.randint(1, 3)))
            article.publishers.set(
                random.sample(authors, k=random.randint(1, 2))
            )

        self.stdout.write(self.style.SUCCESS("Database successfully seeded!"))

    def _clear_db(self):
        Article.objects.all().delete()
        Topic.objects.all().delete()
        Redactor.objects.all().delete()
