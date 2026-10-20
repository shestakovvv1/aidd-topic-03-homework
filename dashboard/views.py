from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ShareModelForm, WatchlistForm
from .models import Share, Watchlist, WatchlistNotification
from .services.graph import get_graph


class ShareListView(ListView):
    """Список акций"""

    model = Share
    template_name = "dashboard/list.html"
    paginate_by = 100
    ordering = ["name"]


class ShareDetailView(View):
    @staticmethod
    def get(request, pk):
        share = Share.objects.get(id=pk)

        return render(
            request,
            "dashboard/detail.html",
            {"plot_div": get_graph(share), "share": share},
        )


class ShareCreateView(LoginRequiredMixin, CreateView):
    """Добавление инструмента"""

    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")


class ShareUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование инструмента"""

    model = Share
    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")


class ShareDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление задачи"""

    model = Share
    template_name = "dashboard/delete.html"
    success_url = reverse_lazy("dashboard:index")


class WatchlistListView(LoginRequiredMixin, ListView):
    """Список наблюдения пользователя"""

    model = Watchlist
    template_name = "dashboard/watchlist.html"
    context_object_name = "watchlist_items"

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user, is_active=True).select_related('share')


class WatchlistCreateView(LoginRequiredMixin, CreateView):
    """Добавление акции в список наблюдения"""

    template_name = "dashboard/watchlist_create.html"
    form_class = WatchlistForm
    success_url = reverse_lazy("dashboard:watchlist")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class WatchlistDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление из списка наблюдения"""

    model = Watchlist
    template_name = "dashboard/watchlist_delete.html"
    success_url = reverse_lazy("dashboard:watchlist")

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)


class NotificationListView(LoginRequiredMixin, ListView):
    """Список уведомлений пользователя"""

    model = WatchlistNotification
    template_name = "dashboard/notifications.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return WatchlistNotification.objects.filter(
            watchlist__user=self.request.user
        ).select_related('watchlist', 'watchlist__share').order_by('-triggered_at')


class NotificationMarkReadView(LoginRequiredMixin, View):
    """Пометить уведомление как прочитанное"""

    @staticmethod
    def post(request, pk):
        notification = WatchlistNotification.objects.get(
            id=pk, watchlist__user=request.user
        )
        notification.is_read = True
        notification.save()
        return redirect("dashboard:notifications")
