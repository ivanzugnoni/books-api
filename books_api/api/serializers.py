from rest_framework import serializers

from books.models import Author, Collaborator, Book


class AuthorSerializer(serializers.ModelSerializer):
    books = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ("id", "name", "created", "biography", "birthday", "books")

    def get_books(self, obj):
        return BaseBookSerializer(obj.books.order_by("name"), many=True).data


class BaseBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "name",
            "created",
            "publish_date",
        )


class BookSerializer(BaseBookSerializer):
    author = serializers.SerializerMethodField()
    collaborators = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = BaseBookSerializer.Meta.fields + ("author", "collaborators")

    def get_author(self, obj):
        return {
            "id": str(obj.author.id),
            "name": obj.author.name,
        }

    def get_collaborators(self, obj):
        return CollaboratorSerializer(obj.collaborators.all(), many=True).data


class CollaboratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaborator
        fields = (
            "id",
            "name",
        )
