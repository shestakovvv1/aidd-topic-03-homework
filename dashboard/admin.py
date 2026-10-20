from django.contrib import admin

from dashboard.models import Portfolio, PortfolioOperation, Share


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("figi", "isin", "name", "ticker", "currency", "last_price")
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


class PortfolioOperationInline(admin.TabularInline):
    model = PortfolioOperation
    extra = 0


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at", "updated_at")
    search_fields = ("name", "user__username", "user__email")
    inlines = [PortfolioOperationInline]


@admin.register(PortfolioOperation)
class PortfolioOperationAdmin(admin.ModelAdmin):
    list_display = (
        "portfolio",
        "share",
        "operation_type",
        "quantity",
        "price",
        "created_at",
    )
    list_filter = ("operation_type",)
