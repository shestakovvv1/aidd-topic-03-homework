from django.contrib import admin

from dashboard.models import Share, Watchlist, WatchlistNotification


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("figi", "isin", "name", "ticker", "currency")
    search_fields = ("figi", "isin", "name", "ticker")
    fields = (
        "figi",
        "isin",
        "name",
        "ticker",
        "currency",
        "uid",
        "last_price",
        "is_trend_high",
    )


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "share", "target_price", "target_type", "is_active")
    list_filter = ("target_type", "is_active")
    search_fields = ("user__email", "share__ticker", "share__name")


@admin.register(WatchlistNotification)
class WatchlistNotificationAdmin(admin.ModelAdmin):
    list_display = ("watchlist", "triggered_price", "triggered_at", "is_read")
    list_filter = ("is_read",)
    readonly_fields = ("triggered_at",)
