from datetime import date
from freezegun import freeze_time
from django.test import TestCase

from books.tests.fixtures import AuthorFactory, CollaboratorFactory, BookFactory


class TestAuthor(TestCase):
    def setUp(self):
        super().setUp()
        self.author_1 = AuthorFactory(
            name="Jorge Luis Borges", birthday=date(1889, 8, 24)
        )

    def test_author_age(self):
        """Should return the author's age based on his birthday"""
        self.assertEqual(self.author_1.birthday, date(1889, 8, 24))

        with freeze_time("2023-01-01T10:00:00"):
            self.assertEqual(self.author_1.age, 133)
