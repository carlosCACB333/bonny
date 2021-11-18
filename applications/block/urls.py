from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"profile", EmployeUserViewset, "profile")


app_name = "profile"
urlpatterns = [
    path("", include(router.urls)),
]
