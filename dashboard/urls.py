from django.urls import include, path

from dashboard.views import (
    PortfolioCreateView,
    PortfolioDeleteView,
    PortfolioDetailView,
    PortfolioListView,
    PortfolioOperationCreateView,
    PortfolioOperationDeleteView,
    ShareCreateView,
    ShareDeleteView,
    ShareDetailView,
    ShareListView,
    ShareUpdateView,
)

app_name = "dashboard"

urlpatterns = [
    path("", ShareListView.as_view(), name="index"),
    path("create", ShareCreateView.as_view(), name="create"),
    path("update/<int:pk>", ShareUpdateView.as_view(), name="update"),
    path("delete/<int:pk>", ShareDeleteView.as_view(), name="delete"),
    path("portfolio/", PortfolioListView.as_view(), name="portfolio_list"),
    path("portfolio/create/", PortfolioCreateView.as_view(), name="portfolio_create"),
    path(
        "portfolio/<int:pk>/",
        PortfolioDetailView.as_view(),
        name="portfolio_detail",
    ),
    path(
        "portfolio/<int:pk>/delete/",
        PortfolioDeleteView.as_view(),
        name="portfolio_delete",
    ),
    path(
        "portfolio/<int:pk>/operations/",
        PortfolioOperationCreateView.as_view(),
        name="portfolio_operation_create",
    ),
    path(
        "portfolio/<int:pk>/operations/<int:operation_id>/delete/",
        PortfolioOperationDeleteView.as_view(),
        name="portfolio_operation_delete",
    ),
    path("api/", include("dashboard.api.urls")),
    path("<int:pk>", ShareDetailView.as_view(), name="detail"),
]
