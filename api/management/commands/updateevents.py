from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import F

from api.models import SectionEvent


class Command(BaseCommand):

    def handle(self, *args, **options) -> None:
        queryset = SectionEvent.objects.filter(datetime__lte=timezone.now()).update(is_active=False)
