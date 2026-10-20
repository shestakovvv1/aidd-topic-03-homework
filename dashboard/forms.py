from django import forms

from .models import Portfolio, PortfolioOperation, Share


class ShareModelForm(forms.ModelForm):
    """Инструмент"""

    class Meta:
        model = Share
        fields = "__all__"


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class PortfolioOperationForm(forms.ModelForm):
    class Meta:
        model = PortfolioOperation
        fields = ("share", "operation_type", "quantity", "price", "note")
        widgets = {
            "share": forms.Select(attrs={"class": "form-control"}),
            "operation_type": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.0001", "min": "0"}
            ),
            "note": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["share"].queryset = Share.objects.order_by("ticker")
        self.fields["share"].label_from_instance = (
            lambda obj: f"{obj.ticker} — {obj.name}"
        )
