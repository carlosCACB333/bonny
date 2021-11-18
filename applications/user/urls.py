from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.api import *

router = DefaultRouter()
router.register(r"employe", EmployeUserViewset, "employe")
router.register(r"test", TestApiView, "test")

app_name = "user"
urlpatterns = [
    path("login/", UserLoginApiView.as_view(), name="user_login"),
    path("logout/", UserLogoutApiView.as_view(), name="user_logout"),
    path("signup/", CompanyUserSignupApiView.as_view(), name="user_signup"),
    path("checkToken/", CheckTokenApiView.as_view(), name="user_check_token"),
    path(
        "company/profile/update/<int:pk>",
        CompanyUserProfileUpdateApiview.as_view(),
        name="profile_update_company",
    ),
    path(
        "employe/profile/update/<int:pk>",
        EmployeUserProfileUpdateApiview.as_view(),
        name="profile_update_employe",
    ),
    path("password/reset/", PasswordResetApiView.as_view(), name="password_reset"),
    path("", include(router.urls)),
]
