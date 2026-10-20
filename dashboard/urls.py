from django.urls import include, path

from dashboard.views import (
    ShareCreateView,
    ShareDeleteView,
    ShareDetailView,
    ShareListView,
    ShareUpdateView,
    WatchlistListView,
    WatchlistCreateView,
    WatchlistDeleteView,
    NotificationListView,
    NotificationMarkReadView,
)

app_name = "dashboard"

urlpatterns = [
    path("", ShareListView.as_view(), name="index"),
    path("<int:pk>", ShareDetailView.as_view(), name="detail"),
    path("create", ShareCreateView.as_view(), name="create"),
    path("update/<int:pk>", ShareUpdateView.as_view(), name="update"),
    path("delete/<int:pk>", ShareDeleteView.as_view(), name="delete"),
    path("watchlist/", WatchlistListView.as_view(), name="watchlist"),
    path("watchlist/create", WatchlistCreateView.as_view(), name="watchlist_create"),
    path("watchlist/delete/<int:pk>", WatchlistDeleteView.as_view(), name="watchlist_delete"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("notifications/<int:pk>/mark-read", NotificationMarkReadView.as_view(), name="notification_mark_read"),
    path("api/", include("dashboard.api.urls")),
]
