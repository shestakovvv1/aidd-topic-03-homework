from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError


class Share(models.Model):
    """Акция"""

    figi = models.CharField(max_length=255, unique=True)
    isin = models.CharField(max_length=255)
    name = models.CharField(max_length=255, verbose_name="Наименование компании")
    ticker = models.CharField(max_length=10, unique=True, verbose_name="Тикер")
    currency = models.CharField(max_length=20, verbose_name="Валюта")
    uid = models.CharField(max_length=255, unique=True)
    last_price = models.FloatField(blank=True, null=True, verbose_name="Текущая цена")
    is_trend_high = models.BooleanField(
        blank=True, null=True, verbose_name="Растет цена"
    )
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    def __str__(self):
        return f"{self.ticker} — {self.name}"


class Portfolio(models.Model):
    """Виртуальный инвестиционный портфель"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolios",
        verbose_name="Владелец",
    )
    name = models.CharField(max_length=255, verbose_name="Название портфеля")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Портфель"
        verbose_name_plural = "Портфели"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_positions(self):
        """Агрегированные позиции: тикер -> qty, avg_price, invested, market_value, pnl."""
        operations = self.operations.select_related("share").order_by("created_at", "id")
        positions = {}

        for op in operations:
            key = op.share_id
            if key not in positions:
                positions[key] = {
                    "share": op.share,
                    "quantity": Decimal("0"),
                    "total_cost": Decimal("0"),
                }
            pos = positions[key]
            qty = Decimal(str(op.quantity))
            price = Decimal(str(op.price))

            if op.operation_type == PortfolioOperation.BUY:
                pos["total_cost"] += qty * price
                pos["quantity"] += qty
            else:
                if pos["quantity"] > 0:
                    avg = pos["total_cost"] / pos["quantity"]
                    pos["total_cost"] -= qty * avg
                pos["quantity"] -= qty

        result = []
        for pos in positions.values():
            qty = pos["quantity"]
            if qty <= 0:
                continue
            avg_price = pos["total_cost"] / qty if qty else Decimal("0")
            last = pos["share"].last_price
            last_price = Decimal(str(last)) if last is not None else None
            invested = avg_price * qty
            market_value = (last_price * qty) if last_price is not None else None
            pnl = (market_value - invested) if market_value is not None else None
            result.append(
                {
                    "share": pos["share"],
                    "quantity": qty,
                    "avg_price": avg_price,
                    "invested": invested,
                    "last_price": last_price,
                    "market_value": market_value,
                    "pnl": pnl,
                }
            )
        return result

    def get_summary(self):
        positions = self.get_positions()
        invested = sum((p["invested"] for p in positions), Decimal("0"))
        market_values = [p["market_value"] for p in positions if p["market_value"] is not None]
        has_all_prices = len(market_values) == len(positions) and len(positions) > 0
        market_value = sum(market_values, Decimal("0")) if positions else Decimal("0")
        if positions and not has_all_prices:
            known = sum(
                (p["market_value"] for p in positions if p["market_value"] is not None),
                Decimal("0"),
            )
            market_value = known
        pnl = market_value - invested if positions else Decimal("0")
        return {
            "positions": positions,
            "invested": invested,
            "market_value": market_value,
            "pnl": pnl,
        }


class PortfolioOperation(models.Model):
    """Операция покупки/продажи в портфеле"""

    BUY = "buy"
    SELL = "sell"
    OPERATION_CHOICES = [
        (BUY, "Покупка"),
        (SELL, "Продажа"),
    ]

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="operations",
        verbose_name="Портфель",
    )
    share = models.ForeignKey(
        Share,
        on_delete=models.PROTECT,
        related_name="portfolio_operations",
        verbose_name="Акция",
    )
    operation_type = models.CharField(
        max_length=4,
        choices=OPERATION_CHOICES,
        verbose_name="Тип операции",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(
        max_digits=14, decimal_places=4, verbose_name="Цена за штуку"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата операции")
    note = models.CharField(max_length=255, blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Операция портфеля"
        verbose_name_plural = "Операции портфеля"
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.get_operation_type_display()} {self.share.ticker} x{self.quantity}"

    def clean(self):
        if self.operation_type == self.SELL and self.portfolio_id and self.share_id:
            held = self._held_quantity()
            if self.quantity > held:
                raise ValidationError(
                    {
                        "quantity": (
                            f"Недостаточно акций для продажи. "
                            f"Доступно: {held}, запрошено: {self.quantity}."
                        )
                    }
                )

    def _held_quantity(self):
        buys = (
            self.portfolio.operations.filter(
                share=self.share, operation_type=self.BUY
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )
        sells = (
            self.portfolio.operations.filter(
                share=self.share, operation_type=self.SELL
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )
        if self.pk:
            current = PortfolioOperation.objects.filter(pk=self.pk).first()
            if current:
                if current.operation_type == self.BUY:
                    buys -= current.quantity
                else:
                    sells -= current.quantity
        return buys - sells
