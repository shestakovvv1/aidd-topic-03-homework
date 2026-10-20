from django import forms

from .models import Share, Watchlist


class ShareModelForm(forms.ModelForm):
    """Инструмент"""

    class Meta:
        model = Share
        fields = "__all__"


class WatchlistForm(forms.ModelForm):
    """Форма для добавления акции в список наблюдения"""

    class Meta:
        model = Watchlist
        fields = ['share', 'target_price', 'target_type']
        widgets = {
            'target_price': forms.NumberInput(attrs={'step': '0.01'}),
        }
