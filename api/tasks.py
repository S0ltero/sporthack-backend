from django.utils import timezone

from celery.utils.log import get_task_logger

from sporthack.celery import app
from .models import SectionEvent, SectionTraining, SectionMember

logger = get_task_logger(__name__)

@app.task
def update_trainings():
    queryset = SectionEvent.objects.filter(datetime__lte=timezone.now()).update(is_active=False)
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

@app.task
def update_events():
    queryset = SectionEvent.objects.filter(datetime__lte=timezone.now()).update(is_active=False)
