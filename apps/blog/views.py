# Create your views here.
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Article, Category, UserProfile, Bookmark, SearchQuery
from .forms import CommentForm
import json
from datetime import timedelta


class HomeView(ListView):
    model = Article
    template_name = "blog/homepage.html"
    context_object_name = "latest_posts"
    paginate_by = 9

    def get_queryset(self):
        return (
            Article.objects.filter(status="published")
            .select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_posts"] = Article.objects.filter(
            status="published", featured=True
        ).select_related("author", "category")[:5]
        context["popular_posts"] = Article.objects.filter(status="published").order_by(
            "-view_count"
        )[:5]
        context["categories"] = Category.objects.annotate(
            article_count=Count("articles")
        )
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("author", "category")
            .prefetch_related("tags", "comments__user")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()

        # Increment view count
        article.increment_view_count()

        context["related_articles"] = article.get_related_articles()
        context["comments"] = article.comments.filter(
            is_approved=True, parent__isnull=True
        ).select_related("user")

        if self.request.user.is_authenticated:
            context["is_bookmarked"] = Bookmark.objects.filter(
                user=self.request.user, article=article
            ).exists()
            context["comment_form"] = CommentForm()

        return context


class ArticleStatisticsView(View):
    def get(self, request, *args, **kwargs):
        # Logic for rendering statistics
        context = {"statistics": "Your statistics data"}
        return render(request, "admin/article_statistics.html", context)


class CategoryListView(ListView):
    model = Category
    template_name = "blog/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.annotate(article_count=Count("articles")).order_by(
            "order", "name"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_categories"] = self.get_queryset().count()
        context["total_articles"] = Article.objects.filter(status="published").count()
        context["total_authors"] = UserProfile.objects.count()
        context["total_views"] = Article.objects.aggregate(
            total_views=Sum("view_count")
        )["total_views"]
        return context


class AuthorProfileView(DetailView):
    model = UserProfile
    template_name = "blog/author_profile.html"
    context_object_name = "author"
    slug_field = "user__username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_object()

        # Get author statistics
        context["author_stats"] = {
            "total_articles": author.user.articles.count(),
            "total_views": author.user.articles.aggregate(
                total_views=Sum("view_count")
            )["total_views"]
            or 0,
            "total_comments": author.user.articles.aggregate(
                total_comments=Count("comments")
            )["total_comments"],
            "total_likes": author.user.articles.aggregate(
                total_likes=Count("bookmarks")
            )["total_likes"],
        }

        # Get monthly activity data
        monthly_activity = []
        for i in range(12):
            date = timezone.now() - timedelta(days=30 * i)
            count = author.user.articles.filter(
                created_at__year=date.year, created_at__month=date.month
            ).count()
            monthly_activity.append({"month": date.strftime("%B %Y"), "count": count})
        context["author_stats"]["monthly_activity"] = json.dumps(
            {
                "labels": [item["month"] for item in reversed(monthly_activity)],
                "articles": [item["count"] for item in reversed(monthly_activity)],
            }
        )

        # Get latest articles
        context["latest_articles"] = author.user.articles.filter(
            status="published"
        ).order_by("-published_at")[:6]

        # Get recent activities
        context["recent_activities"] = []

        # Articles
        for article in author.user.articles.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ):
            context["recent_activities"].append(
                {
                    "action": "Published article",
                    "timestamp": article.published_at,
                    "description": article.title,
                }
            )

        # Comments
        for comment in author.user.comments.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ):
            context["recent_activities"].append(
                {
                    "action": "Commented on",
                    "timestamp": comment.created_at,
                    "description": comment.article.title,
                }
            )

        # Sort activities by timestamp
        context["recent_activities"].sort(key=lambda x: x["timestamp"], reverse=True)

        return context


class SearchResultsView(TemplateView):
    template_name = "blog/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")

        if query:
            # Log search query
            if self.request.user.is_authenticated:
                user = self.request.user
            else:
                user = None

            start_time = timezone.now()

            # Perform search
            results = (
                Article.objects.filter(
                    Q(title__icontains=query)
                    | Q(content__icontains=query)
                    | Q(excerpt__icontains=query)
                    | Q(tags__name__icontains=query)
                )
                .filter(status="published")
                .distinct()
            )

            # Apply filters
            categories = self.request.GET.getlist("category")
            if categories:
                results = results.filter(category__slug__in=categories)

            tags = self.request.GET.getlist("tag")
            if tags:
                results = results.filter(tags__slug__in=tags)

            authors = self.request.GET.getlist("author")
            if authors:
                results = results.filter(author__username__in=authors)

            date_range = self.request.GET.get("date_range")
            if date_range:
                start_date, end_date = date_range.split(" - ")
                results = results.filter(published_at__range=[start_date, end_date])

            # Sort results
            sort = self.request.GET.get("sort", "relevance")
            if sort == "date":
                results = results.order_by("-published_at")
            elif sort == "views":
                results = results.order_by("-view_count")

            end_time = timezone.now()
            search_time = (end_time - start_time).total_seconds() * 1000

            # Log search query
            SearchQuery.objects.create(
                query=query, user=user, results_count=results.count()
            )

            # Pagination
            paginator = Paginator(results, 10)
            page = self.request.GET.get("page", 1)
            results = paginator.get_page(page)

            context.update(
                {
                    "query": query,
                    "results": results,
                    "total_results": paginator.count,
                    "search_time": round(search_time, 2),
                    "categories": Category.objects.all(),
                    "popular_tags": Article.tags.most_common()[:20],
                    "related_searches": SearchQuery.objects.filter(
                        created_at__gte=timezone.now() - timedelta(days=30)
                    )
                    .values("query")
                    .annotate(count=Count("query"))
                    .order_by("-count")[:5],
                    "search_trends": self.get_search_trends(),
                }
            )

        return context

    def get_search_trends(self):
        trends = []
        for i in range(7):
            date = timezone.now() - timedelta(days=i)
            count = SearchQuery.objects.filter(created_at__date=date.date()).count()
            trends.append({"date": date.strftime("%Y-%m-%d"), "count": count})

        return json.dumps(
            {
                "labels": [item["date"] for item in reversed(trends)],
                "data": [item["count"] for item in reversed(trends)],
            }
        )
