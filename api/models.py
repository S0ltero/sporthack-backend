from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core import validators
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import StudentManager, TrainerManager


class User(AbstractUser, UserManager):

    SEX_CHOICES = [
        ("MEN", "Мужской"),
        ("WOMEN", "Женский")
    ]

    username = None
    email = models.EmailField(
        _("Email адрес"),
        unique=True,
        validators=[validators.validate_email],
        error_messages={
            "unique": _("Пользователь с таким email уже существует."),
        },
    )
    image = models.ImageField(
        _("Фотография"),
        upload_to="user/",
        default="user/no-image.png",
        blank=True,
    )
    middle_name = models.CharField(verbose_name=_("Отчество"), max_length=30, blank=True)
    sex = models.CharField(verbose_name=_("Пол"), max_length=5, choices=SEX_CHOICES)
    institution = models.TextField(verbose_name=_("Учебное заведение"), blank=True)
    group = models.CharField(verbose_name=_("Группа"), max_length=50, blank=True)
    rank = models.TextField(verbose_name=_("Звание"), blank=True)
    phone = models.CharField(verbose_name=_("Номер телефона"), max_length=255, blank=True)
    is_trainer = models.BooleanField(verbose_name=_("Тренер"), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ("first_name", "last_name")

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return f"(User: {self.id} - {self.username})"


class Student(User):
    objects = StudentManager()
    class Meta:
        proxy = True
        verbose_name = _("Студент")
        verbose_name_plural = _("Студенты")


class Trainer(User):
    objects = TrainerManager()
    class Meta:
        proxy = True
        verbose_name = _("Тренер")
        verbose_name_plural = _("Тренеры")

    def save(self) -> None:
        self.is_trainer = True
        return super().save(self)


class Section(models.Model):
    trainers = models.ManyToManyField(Trainer, verbose_name=_("Тренеры"),
                                related_name="trainers",)
    title = models.CharField(_("Название секции"), max_length=255)
    description = models.TextField(_("Описание секции"))
    image = models.ImageField(
        _("Изображение"),
        upload_to="section/",
        default="section/no-image.png",
        blank=True,
    )

    class Meta:
        verbose_name = _("Секция")
        verbose_name_plural = _("Секции")


class SectionMember(models.Model):
    section = models.ForeignKey(Section, related_name="member", 
                                on_delete=models.CASCADE)
    member = models.ForeignKey(Student, related_name="section_member",
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Участник секции")
        verbose_name_plural = _("Участники секции")
        unique_together = ['section', 'member']


class SectionEvent(models.Model):
    section = models.ForeignKey(Section, related_name="event",
                                on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_("Название"), max_length=255)
    level = models.CharField(verbose_name=_("Уровень"), max_length=100)
    datetime = models.DateTimeField(verbose_name=_("Дата проведения"))
    place = models.TextField(verbose_name=_("Место проведения"))
    is_active = models.BooleanField(verbose_name=_("Активно?"), default=True)

    class Meta:
        verbose_name = _("Мероприятие")
        verbose_name_plural = _("Мероприятия")


class EventMember(models.Model):
    event = models.ForeignKey(SectionEvent, related_name="member",
                              on_delete=models.CASCADE)
    member = models.ForeignKey(Student, related_name="event_member",
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Участник мероприятия")
        verbose_name_plural = _("Участники мероприятия")
        unique_together = ['event', 'member']


class SectionTraining(models.Model):
    section = models.ForeignKey(Section, related_name="training",
                                on_delete=models.CASCADE)
    datetime = models.DateTimeField(verbose_name=_("Дата проведения"))
    
    def generate_hash_url(self):
        pass

    class Meta:
        verbose_name = _("Тренировка")
        verbose_name_plural = _("Тренировки")


class TrainingMember(models.Model):
    training = models.ForeignKey(SectionTraining, related_name="member",
                                 on_delete=models.CASCADE)
    member = models.ForeignKey(Student, related_name="training_member",
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Участник тренировки")
        verbose_name_plural = _("Участники тренировки")
        unique_together = ['training', 'member']


class ResetPassCode(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_("Пользователь"),
        related_name="reset_code",
        on_delete=models.CASCADE,
    )
    code = models.IntegerField(verbose_name=_("Код сброса пароля"))
    expired_at = models.DateTimeField(verbose_name=_("Время истечения"), default=timezone.now)

    def save(self, *args, **kwargs):
        self.expired_at = timezone.now() + timezone.timedelta(minutes=30)
        super(ResetPassCode, self).save()