from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import F

from api.models import SectionTraining, SectionMember, Student


class Command(BaseCommand):

    def handle(self, *args, **options) -> None:
        queryset = SectionTraining.objects.filter(datetime__lte=timezone.now(), is_active=True)
        for training in queryset:
            # Update general user rating
            training_members = training.member.all()
            for member in training_members:
                member.user.rating = member.user.rating + training.duration
                member.user.save()
            # Update section member rating
            section_members = SectionMember.objects.filter(section=training.section)
            training_user_ids = training.member.values_list("user", flat=True)
            section_members = section_members.filter(user__in=training_user_ids)
            for member in section_members:
                member.rating = member.rating + training.duration
                member.pass_trainings += 1
                member.save()
        queryset.update(is_active=False)
