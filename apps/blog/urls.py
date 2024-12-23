from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "article/<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"
    ),
    path(
        "category/<slug:slug>/",
        views.CategoryListView.as_view(),
        name="category_detail",
    ),
    path(
        "author/<str:username>/",
        views.AuthorProfileView.as_view(),
        name="author_profile",
    ),
    path("search/", views.SearchResultsView.as_view(), name="search"),
    # paths to about and contact views
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
]
