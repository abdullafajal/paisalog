from django.urls import path
from . import views
from .views import UserProfileUpdateView

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("entries/", views.EntryListView.as_view(), name="entry_list"),
    path("entries/create/", views.EntryCreateView.as_view(), name="entry_create"),
    path("entries/<int:pk>/update/", views.EntryUpdateView.as_view(), name="entry_update"),
    path("entries/<int:pk>/delete/", views.EntryDeleteView.as_view(), name="entry_delete"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/update/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
    path('profile/', UserProfileUpdateView.as_view(), name='profile_update'),
] 