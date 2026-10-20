from django.core.management.base import BaseCommand, CommandError

from config.settings import TINKOFF_TOKEN
from dashboard.models import Share


class Command(BaseCommand):
    help = "Add shares to DB"

    def handle(self, *args, **options):
        if not TINKOFF_TOKEN:
            raise CommandError("Set TINKOFF_TOKEN in config/settings.py first")

        try:
            from tinkoff.invest import Client
        except ImportError as exc:
            raise CommandError(
                "Install tinkoff-investments (or t-tech-investments) to use this command"
            ) from exc

        with Client(TINKOFF_TOKEN) as client:
            shares = client.instruments.shares()
            created = 0
            for share in shares.instruments:
                _, was_created = Share.objects.get_or_create(
                    figi=share.figi,
                    defaults={
                        "name": share.name,
                        "isin": share.isin,
                        "ticker": share.ticker,
                        "currency": share.currency,
                        "uid": share.uid,
                    },
                )
                if was_created:
                    created += 1
            self.stdout.write(self.style.SUCCESS(f"Created {created} shares"))
