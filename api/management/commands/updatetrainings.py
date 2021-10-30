from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import F

from api.models import SectionTraining, Student


class Command(BaseCommand):

    def handle(self, *args, **options) -> None:
        queryset = SectionTraining.objects.filter(datetime__lte=timezone.now(), is_active=True)
        for training in queryset:
            for member in training.member.all():
                member.user.rating = member.user.rating + training.duration
                member.user.save()
        queryset.update(is_active=False)
