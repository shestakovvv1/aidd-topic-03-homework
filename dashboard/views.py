from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from .forms import PortfolioForm, PortfolioOperationForm, ShareModelForm
from .models import Portfolio, PortfolioOperation, Share
from .services.graph import get_graph


class IsUserAuthenticatedMixin(LoginRequiredMixin):
    """Требует аутентификации; неавторизованных отправляет на страницу входа."""

    login_url = reverse_lazy("user:auth")
    redirect_field_name = None


class ShareListView(ListView):
    """Список акций"""

    model = Share
    template_name = "dashboard/list.html"
    paginate_by = 100
    ordering = ["name"]


class ShareDetailView(View):
    @staticmethod
    def get(request, pk):
        share = get_object_or_404(Share, id=pk)
        return render(
            request,
            "dashboard/detail.html",
            {"plot_div": get_graph(share), "share": share},
        )


class ShareCreateView(IsUserAuthenticatedMixin, CreateView):
    """Добавление инструмента"""

    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")


class ShareUpdateView(IsUserAuthenticatedMixin, UpdateView):
    """Редактирование инструмента"""

    model = Share
    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")


class ShareDeleteView(IsUserAuthenticatedMixin, DeleteView):
    """Удаление акции"""

    model = Share
    template_name = "dashboard/delete.html"
    success_url = reverse_lazy("dashboard:index")


class PortfolioOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("user:auth")
    redirect_field_name = None

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

    def test_func(self):
        return self.request.user.is_authenticated


class PortfolioListView(PortfolioOwnerMixin, ListView):
    """Список портфелей пользователя"""

    model = Portfolio
    template_name = "dashboard/portfolio_list.html"
    context_object_name = "portfolios"

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)


class PortfolioCreateView(IsUserAuthenticatedMixin, CreateView):
    """Создание портфеля"""

    model = Portfolio
    form_class = PortfolioForm
    template_name = "dashboard/portfolio_form.html"
    success_url = reverse_lazy("dashboard:portfolio_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Портфель создан.")
        return super().form_valid(form)


class PortfolioDetailView(PortfolioOwnerMixin, DetailView):
    """Детали портфеля: позиции, P&L, история операций"""

    model = Portfolio
    template_name = "dashboard/portfolio_detail.html"
    context_object_name = "portfolio"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = self.object.get_summary()
        context.update(summary)
        context["operations"] = self.object.operations.select_related("share")
        context["operation_form"] = PortfolioOperationForm()
        return context


class PortfolioDeleteView(PortfolioOwnerMixin, DeleteView):
    """Удаление портфеля"""

    model = Portfolio
    template_name = "dashboard/portfolio_confirm_delete.html"
    success_url = reverse_lazy("dashboard:portfolio_list")


class PortfolioOperationCreateView(IsUserAuthenticatedMixin, View):
    """Добавление операции покупки/продажи"""

    def post(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        form = PortfolioOperationForm(request.POST)
        if form.is_valid():
            operation = form.save(commit=False)
            operation.portfolio = portfolio
            try:
                operation.full_clean()
                operation.save()
                messages.success(request, "Операция добавлена.")
            except ValidationError as exc:
                for err_list in exc.message_dict.values():
                    for err in err_list:
                        messages.error(request, err)

        else:
            messages.error(request, "Проверьте данные операции.")
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
        return redirect("dashboard:portfolio_detail", pk=portfolio.pk)


class PortfolioOperationDeleteView(IsUserAuthenticatedMixin, View):
    """Удаление операции из истории"""

    def post(self, request, pk, operation_id):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        operation = get_object_or_404(
            PortfolioOperation, pk=operation_id, portfolio=portfolio
        )
        operation.delete()
        messages.success(request, "Операция удалена.")
        return redirect("dashboard:portfolio_detail", pk=portfolio.pk)
