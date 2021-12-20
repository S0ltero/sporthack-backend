from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings

from .models import StudentAward, Student
from .email import AwardSuccessVerified, AwardNoVerified


@receiver(pre_save, sender=StudentAward)
def on_award_update(sender, instance, **kwargs):
    if instance.id is None:
        return

    current = instance
    previous = StudentAward.objects.get(pk=instance.pk)
    if previous.verified != current.verified and current.verified == True:
        context = {"award_title": instance.title, "domain": settings.SITE_DOMAIN}
        to = [instance.user.email]
        AwardSuccessVerified(context=context).send(to)


@receiver(post_delete, sender=StudentAward)
def on_award_delete(sender, instance, **kwargs):
    try:
        Student.objects.get(pk=instance.user.id)
    except Student.DoesNotExist:
        return
    context = {"award_title": instance.title, "domain": settings.SITE_DOMAIN}
    to = [instance.user.email]
    AwardNoVerified(context=context).send(to)