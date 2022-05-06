from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings

from .models import StudentAward
from .email import AwardSuccessVerified


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
