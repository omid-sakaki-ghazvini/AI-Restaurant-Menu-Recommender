import json
from pathlib import Path

from django.core.management.base import BaseCommand

from recommender.models import MenuItem


class Command(BaseCommand):
    help = "Load initial menu data from JSON file"

    def handle(self, *args, **options):
        path = Path(__file__).resolve().parents[3] / "data" / "menu_seed.json"

        if not path.exists():
            self.stdout.write(self.style.ERROR(f"File not found: {path}"))
            return

        with open(path, encoding="utf-8") as f:
            items = json.load(f)

        created = 0
        for item in items:
            obj, was_created = MenuItem.objects.get_or_create(
                name=item["name"],
                defaults=item
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Loaded {created} new items. Total: {MenuItem.objects.count()}"
        ))