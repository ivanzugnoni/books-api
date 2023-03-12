import uuid
from freezegun import freeze_time
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Author
from books.tests.fixtures import AuthorFactory, CollaboratorFactory, BookFactory


@freeze_time("2023-01-20T10:00:00")
class AuthorTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = User.objects.create(username="user_1", is_staff=False)
        self.user_2 = User.objects.create(username="user_2", is_staff=True)

        self.author_1 = AuthorFactory(name="J. K. Rowling")
        self.author_2 = AuthorFactory(name="Jorge Luis Borges")
        self.author_3 = AuthorFactory(name="George R. R. Martin")

        self.collaborator_1 = CollaboratorFactory()
        self.collaborator_2 = CollaboratorFactory()

        self.book_1 = BookFactory(author=self.author_1, name="Book 1")
        self.book_2 = BookFactory(author=self.author_1, name="Book 2")
        self.book_3 = BookFactory(author=self.author_2, name="Book 3")

    def test_authors_list(self):
        """Should return the list of all authors paginated and ordered by name"""
        # preconditions
        self.client.force_login(self.user_1)
        self.assertEqual(self.user_1.is_staff, False)
        self.assertEqual(Author.objects.count(), 3)

        expected = {
            "count": 3,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": str(self.author_3.id),
                    "name": self.author_3.name,
                    "biography": self.author_3.biography,
                    "birthday": self.author_3.birthday.isoformat(),
                    "created": "2023-01-20T10:00:00Z",
                    "books": [],
                },
                {
                    "id": str(self.author_1.id),
                    "name": self.author_1.name,
                    "biography": self.author_1.biography,
                    "birthday": self.author_1.birthday.isoformat(),
                    "created": "2023-01-20T10:00:00Z",
                    "books": [
                        {
                            "id": str(self.book_1.id),
                            "name": self.book_1.name,
                            "publish_date": self.book_1.publish_date.isoformat(),
                            "created": "2023-01-20T10:00:00Z",
                        },
                        {
                            "id": str(self.book_2.id),
                            "name": self.book_2.name,
                            "publish_date": self.book_2.publish_date.isoformat(),
                            "created": "2023-01-20T10:00:00Z",
                        },
                    ],
                },
                {
                    "id": str(self.author_2.id),
                    "name": self.author_2.name,
                    "biography": self.author_2.biography,
                    "birthday": self.author_2.birthday.isoformat(),
                    "created": "2023-01-20T10:00:00Z",
                    "books": [
                        {
                            "id": str(self.book_3.id),
                            "name": self.book_3.name,
                            "publish_date": self.book_3.publish_date.isoformat(),
                            "created": "2023-01-20T10:00:00Z",
                        }
                    ],
                },
            ],
        }
        response = self.client.get("/api/v1/authors")

        # postconditions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected)

    def test_authors_list_not_authenticated(self):
        """Should return 403 when listing authors as anonymous user"""
        # preconditions
        self.client.logout()

        response = self.client.get("/api/v1/authors")

        # postconditions
        expected = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), expected)

    def test_authors_retrieve(self):
        """Should return the author with given id"""
        # preconditions
        self.client.force_login(self.user_1)
        self.assertEqual(self.user_1.is_staff, False)

        expected = {
            "id": str(self.author_1.id),
            "name": self.author_1.name,
            "biography": self.author_1.biography,
            "birthday": self.author_1.birthday.isoformat(),
            "created": "2023-01-20T10:00:00Z",
            "books": [
                {
                    "id": str(self.book_1.id),
                    "name": self.book_1.name,
                    "publish_date": self.book_1.publish_date.isoformat(),
                    "created": "2023-01-20T10:00:00Z",
                },
                {
                    "id": str(self.book_2.id),
                    "name": self.book_2.name,
                    "publish_date": self.book_2.publish_date.isoformat(),
                    "created": "2023-01-20T10:00:00Z",
                },
            ],
        }
        response = self.client.get(f"/api/v1/authors/{self.author_1.id}")

        # postconditions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected)

    def test_authors_retrieve_not_authenticated(self):
        """Should return 403 when retrieving authors as anonymous user"""
        # preconditions
        self.client.logout()

        response = self.client.get(f"/api/v1/authors/{self.author_1.id}")

        # postconditions
        expected = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), expected)

    def test_authors_retrieve_not_found(self):
        """Should return 404 when author with given id is not found"""
        # preconditions
        self.client.force_login(self.user_1)
        self.assertEqual(self.user_1.is_staff, False)

        invalid_id = uuid.uuid4()
        response = self.client.get(f"/api/v1/authors/{invalid_id}")

        # postconditions
        expected = {"detail": f"Author with id '{invalid_id}' was not found."}
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), expected)

    def test_authors_create(self):
        """Should create a new author when provided data is valid"""
        # preconditions
        self.client.force_login(self.user_2)
        self.assertEqual(self.user_2.is_staff, True)
        self.assertEqual(Author.objects.count(), 3)
        self.assertFalse(Author.objects.filter(name="New author").exists())

        payload = {
            "name": "New author",
            "biography": "Some bio here",
            "birthday": "1950-12-25",
        }
        with freeze_time("2023-01-20T10:00:00"):
            response = self.client.post("/api/v1/authors", data=payload)

        # postconditions
        self.assertEqual(Author.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_author = Author.objects.get(name="New author")
        self.assertEqual(new_author.name, "New author")
        self.assertEqual(new_author.biography, "Some bio here")
        self.assertEqual(new_author.birthday.isoformat(), "1950-12-25")
        self.assertTrue(
            new_author.created.isoformat().startswith("2023-01-20T10:00:00")
        )

    def test_authors_create_not_authenticated(self):
        """Should return 403 when creating authors as anonymous user"""
        # preconditions
        self.client.logout()

        payload = {
            "name": "New author",
            "biography": "Some bio here",
            "birthday": "1950-12-25",
        }
        response = self.client.post("/api/v1/authors", data=payload)

        # postconditions
        expected = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), expected)

    def test_authors_create_not_staff(self):
        """Should return 403 while creating author with a non-staff user"""
        # preconditions
        self.client.force_login(self.user_1)
        self.assertEqual(self.user_1.is_staff, False)
        self.assertEqual(Author.objects.count(), 3)

        payload = {
            "name": "New author",
            "biography": "Some bio here",
            "birthday": "1950-12-25",
        }
        response = self.client.post("/api/v1/authors", data=payload)

        # postconditions
        expected = {"detail": "You do not have permission to perform this action."}
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authors_create_missing_data(self):
        """Should return 400 while creating author with missing required data in given payload"""
        # preconditions
        self.client.force_login(self.user_2)
        self.assertEqual(self.user_2.is_staff, True)
        self.assertEqual(Author.objects.count(), 3)
        self.assertFalse(Author.objects.filter(name="New author").exists())

        payload = {}
        response = self.client.post("/api/v1/authors", data=payload)

        # postconditions
        self.assertEqual(Author.objects.count(), 3)
        expected = {"name": ["This field is required."]}
        self.assertEqual(response.json(), expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authors_update(self):
        """Should update author with given id when provided data is valid"""
        # preconditions
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(self.author_1.name, "J. K. Rowling")
        self.assertEqual(self.author_1.biography, "Some biography of the author here")
        self.assertTrue(
            self.author_1.created.isoformat().startswith("2023-01-20T10:00:00")
        )
        self.assertTrue(
            self.author_1.modified.isoformat().startswith("2023-01-20T10:00:00")
        )

        payload = {
            "name": "Updated name",
            "biography": "Updated bio",
        }
        with freeze_time("2023-06-30T10:00:00"):
            self.client.force_login(self.user_2)
            response = self.client.put(
                f"/api/v1/authors/{self.author_1.id}", data=payload
            )

        # postconditions
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.author_1.refresh_from_db()
        self.assertEqual(self.author_1.name, "Updated name")
        self.assertEqual(self.author_1.biography, "Updated bio")
        self.assertTrue(
            self.author_1.created.isoformat().startswith("2023-01-20T10:00:00")
        )
        self.assertTrue(
            self.author_1.modified.isoformat().startswith("2023-06-30T10:00:00")
        )

    def test_authors_update_not_authenticated(self):
        """Should return 403 when updating authors as anonymous user"""
        # preconditions
        self.client.logout()

        payload = {
            "name": "Updated name",
            "biography": "Updated bio",
        }
        response = self.client.put(f"/api/v1/authors/{self.author_1.id}", data=payload)

        # postconditions
        expected = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), expected)

    def test_authors_update_not_staff(self):
        """Should return 403 while updating author with a non-staff user"""
        # preconditions
        self.client.force_login(self.user_1)
        self.assertEqual(self.user_1.is_staff, False)
        self.assertEqual(Author.objects.count(), 3)

        payload = {
            "name": "Updated name",
            "biography": "Updated bio",
        }
        response = self.client.put(f"/api/v1/authors/{self.author_1.id}", data=payload)

        # postconditions
        expected = {"detail": "You do not have permission to perform this action."}
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authors_update_missing_data(self):
        """Should return 400 while updating author with missing required data in given payload"""
        # preconditions
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(self.author_1.name, "J. K. Rowling")
        self.assertEqual(self.author_1.biography, "Some biography of the author here")
        self.assertTrue(
            self.author_1.created.isoformat().startswith("2023-01-20T10:00:00")
        )
        self.assertTrue(
            self.author_1.modified.isoformat().startswith("2023-01-20T10:00:00")
        )

        payload = {}
        with freeze_time("2023-06-30T10:00:00"):
            self.client.force_login(self.user_2)
            response = self.client.put(
                f"/api/v1/authors/{self.author_1.id}", data=payload
            )

        # postconditions
        self.assertEqual(Author.objects.count(), 3)
        expected = {"name": ["This field is required."]}
        self.assertEqual(response.json(), expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.author_1.refresh_from_db()
        self.assertEqual(self.author_1.name, "J. K. Rowling")
        self.assertEqual(self.author_1.biography, "Some biography of the author here")
        self.assertTrue(
            self.author_1.created.isoformat().startswith("2023-01-20T10:00:00")
        )
        self.assertTrue(
            self.author_1.modified.isoformat().startswith("2023-01-20T10:00:00")
        )

    def test_authors_partial_update(self):
        """Should partial update author with given id when provided data is valid"""
        # preconditions
        self.client.force_login(self.user_2)
        self.assertEqual(self.user_2.is_staff, True)
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(self.author_1.name, "J. K. Rowling")

        payload = {
            "name": "Updated name",
        }
        response = self.client.patch(
            f"/api/v1/authors/{self.author_1.id}", data=payload
        )

        # postconditions
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.author_1.refresh_from_db()
        self.assertEqual(self.author_1.name, "Updated name")

    def test_authors_partial_update_not_authenticated(self):
        """Should return 403 when partial updating authors as anonymous user"""
        # preconditions
        self.client.logout()

        payload = {
            "name": "Updated name",
        }
        response = self.client.patch(
            f"/api/v1/authors/{self.author_1.id}", data=payload
        )

        # postconditions
        expected = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), expected)

    def test_authors_partial_update_not_staff(self):
        """Should return 403 while partial updating author with a non-staff user"""
        # preconditions
        self.client.force_login(self.user_1)
        self.assertEqual(self.user_1.is_staff, False)
        self.assertEqual(Author.objects.count(), 3)

        payload = {
            "name": "Updated name",
        }
        response = self.client.patch(
            f"/api/v1/authors/{self.author_1.id}", data=payload
        )

        # postconditions
        expected = {"detail": "You do not have permission to perform this action."}
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authors_delete(self):
        """Should delete author with given id"""
        # preconditions
        self.client.force_login(self.user_2)
        self.assertEqual(self.user_2.is_staff, True)
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(self.author_1.name, "J. K. Rowling")

        response = self.client.delete(f"/api/v1/authors/{self.author_1.id}")

        # postconditions
        self.assertEqual(Author.objects.count(), 2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Author.objects.filter(name="J. K. Rowling").exists())

    def test_authors_delete_not_authenticated(self):
        """Should return 403 when partial updating authors as anonymous user"""
        # preconditions
        self.client.logout()

        response = self.client.delete(f"/api/v1/authors/{self.author_1.id}")

        # postconditions
        expected = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), expected)

    def test_authors_delete_not_staff(self):
        """Should return 403 while deleting author with a non-staff user"""
        # preconditions
        self.client.force_login(self.user_1)
        self.assertEqual(self.user_1.is_staff, False)
        self.assertEqual(Author.objects.count(), 3)

        response = self.client.delete(f"/api/v1/authors/{self.author_1.id}")

        # postconditions
        expected = {"detail": "You do not have permission to perform this action."}
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authors_delete_not_found(self):
        """Should return 404 when author with given id is not found"""
        # preconditions
        self.client.force_login(self.user_2)
        self.assertEqual(self.user_2.is_staff, True)
        self.assertEqual(Author.objects.count(), 3)
        invalid_id = uuid.uuid4()

        response = self.client.delete(f"/api/v1/authors/{invalid_id}")

        # postconditions
        self.assertEqual(Author.objects.count(), 3)
        expected = {"detail": f"Author with id '{invalid_id}' was not found."}
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), expected)
