from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from books.models import Author, Collaborator, Book
from api.serializers import AuthorSerializer, CollaboratorSerializer, BookSerializer


class AuthorViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return (IsAuthenticated(), IsAdminUser())
        return (IsAuthenticated(),)

    def list(self, request):
        authors = Author.objects.order_by("name")

        # paginate response
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(authors, request)

        serializer = AuthorSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        # validate that author with given id exists
        try:
            author = Author.objects.get(id=pk)
        except Author.DoesNotExist:
            return Response(
                {"detail": f"Author with id '{pk}' was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = AuthorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        author = serializer.save()
        return Response(AuthorSerializer(author).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        # validate that author with given id exists
        try:
            author = Author.objects.get(id=pk)
        except Author.DoesNotExist:
            return Response(
                {"detail": f"Author with id '{pk}' was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AuthorSerializer(author, data=request.data)
        serializer.is_valid(raise_exception=True)
        author = serializer.save()
        return Response(AuthorSerializer(author).data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        # validate that author with given id exists
        try:
            author = Author.objects.get(id=pk)
        except Author.DoesNotExist:
            return Response(
                {"detail": f"Author with id '{pk}' was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AuthorSerializer(author, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        author = serializer.save()
        return Response(AuthorSerializer(author).data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        # validate that author with given id exists
        try:
            author = Author.objects.get(id=pk)
        except Author.DoesNotExist:
            return Response(
                {"detail": f"Author with id '{pk}' was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        author.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
