from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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


class Watchlist(models.Model):
    """Список наблюдения акций пользователя"""

    TARGET_TYPE_CHOICES = [
        ('above', 'Выше'),
        ('below', 'Ниже'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    share = models.ForeignKey(Share, on_delete=models.CASCADE, verbose_name="Акция")
    target_price = models.FloatField(verbose_name="Целевая цена")
    target_type = models.CharField(
        max_length=10,
        choices=TARGET_TYPE_CHOICES,
        verbose_name="Условие"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Список наблюдения"
        verbose_name_plural = "Списки наблюдения"
        unique_together = ['user', 'share']


class WatchlistNotification(models.Model):
    """Уведомления о достижении целевой цены"""

    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, verbose_name="Список наблюдения")
    triggered_price = models.FloatField(verbose_name="Цена срабатывания")
    triggered_at = models.DateTimeField(auto_now_add=True, verbose_name="Время срабатывания")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
