from django.urls import path, include
from rest_framework_nested import routers

from api import views


router = routers.DefaultRouter(trailing_slash=False)
router.register(r"authors", views.AuthorViewSet, basename="authors")


urlpatterns = [
    path("", include(router.urls)),
]
