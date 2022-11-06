from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager, StudentManager, TrainerManager, AdminManager
from .email import AwardNoVerified


class User(AbstractUser):
    username = None
    email = models.EmailField(
        _("Email адрес"),
        unique=True,
        validators=[validators.validate_email],
        error_messages={
            "unique": _("Пользователь с таким email уже существует."),
        },
    )
    photo = models.ImageField(
        _("Фотография"),
        upload_to="user/",
        default="user/no-image.png",
        blank=True,
    )
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    middle_name = models.CharField(verbose_name=_("Отчество"), max_length=30, blank=True)

    # Student unique fields
    institution = models.TextField(verbose_name=_("Учебное заведение"), blank=True)
    group = models.CharField(verbose_name=_("Группа"), max_length=50, blank=True)
    rating = models.IntegerField(verbose_name=_("Рейтинг"), default=0, blank=True, null=True)

    # Trainer unique fields
    rank = models.TextField(verbose_name=_("Звание"), blank=True)
    phone = PhoneNumberField(verbose_name=_("Номер телефона"), blank=True)
    is_trainer = models.BooleanField(verbose_name=_("Тренер"), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ()

    objects = UserManager()

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Student(User):
    objects = StudentManager()
    class Meta:
        proxy = True
        verbose_name = _("Студент")
        verbose_name_plural = _("Студенты")


class StudentAward(models.Model):
    CATEGORY_CHOICES = [
        ("institute", "Институтский"),
        ("university", "Университетсткий"),
        ("regional", "Региональный"),
        ("interregional", "Межрегиональный"),
        ("all-russia", "Всероссийский"),
        ("international", "Международный")
    ]

    user = models.ForeignKey(
        Student,
        verbose_name=_("Студент"),
        related_name="awards",
        related_query_name="award", 
        on_delete=models.CASCADE
    )
    file = models.FileField(
        verbose_name=_("Изображение награды"), 
        upload_to="user/"
    )
    category = models.CharField(
        verbose_name=_("Категория награды"),
        max_length=100,
        choices=CATEGORY_CHOICES
    )
    title = models.CharField(verbose_name=_("Название награды"), max_length=100)
    verified = models.BooleanField(verbose_name=_("Проверено"), default=False)

    class Meta:
        verbose_name = _("Награда")
        verbose_name_plural = _("Награды")

    def delete(self):
        context = {"award_title": self.title, "domain": settings.SITE_DOMAIN}
        to = [self.user.email]
        AwardNoVerified(context=context).send(to)
        return super().delete()


class Trainer(User):
    objects = TrainerManager()
    class Meta:
        proxy = True
        verbose_name = _("Тренер")
        verbose_name_plural = _("Тренеры")

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            return super(Trainer, self).save(*args, **kwargs)
        self.is_trainer = True
        return super().save(self)


class Admin(User):
    objects = AdminManager()

    class Meta:
        proxy = True
        verbose_name = _("Администратор")
        verbose_name_plural = _("Администраторы")


class Section(models.Model):
    trainers = models.ManyToManyField(
        Trainer,
        verbose_name=_("Тренеры"),
        related_name="sections"
    )
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

    def __str__(self):
        return f"{self.title}"


class SectionMember(models.Model):
    section = models.ForeignKey(
        Section,
        related_name="member", 
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        Student,
        verbose_name=_("Участник"),
        related_name="section",
        on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        verbose_name=_("Рейтинг"),
        default=0,
        blank=True
    )
    pass_trainings = models.IntegerField(
        verbose_name=_("Пройденные тренировки"),
        default=0,
        blank=True
    )

    class Meta:
        verbose_name = _("Участник секции")
        verbose_name_plural = _("Участники секции")
        unique_together = ['section', 'user']

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"


class SectionEvent(models.Model):
    LEVEL_CHOICES = [
        ("institute", "Институтский"),
        ("university", "Университетсткий"),
        ("interuniversity", "Межуниверситетский"),
        ("district", "Районный"),
        ("city", "Городской"),
        ("regional", "Областной"),
        ("all-russia", "Всероссийский")
    ]

    section = models.ForeignKey(
        Section,
        verbose_name=_("Секция"), 
        related_name="event",
        on_delete=models.CASCADE
    )
    title = models.CharField(
        verbose_name=_("Название"),
        max_length=255
    )
    level = models.CharField(
        verbose_name=_("Уровень"),
        max_length=100,
        choices=LEVEL_CHOICES
    )
    is_active = models.BooleanField(
        verbose_name=_("Активно?"),
        default=True
    )
    members = models.ManyToManyField(
        Student,
        verbose_name="Участники",
        through="EventMember",
        related_name="events"
    )
    datetime = models.DateTimeField(verbose_name=_("Дата проведения"))
    place = models.TextField(verbose_name=_("Место проведения"))

    class Meta:
        verbose_name = _("Мероприятие")
        verbose_name_plural = _("Мероприятия")


class EventMember(models.Model):
    event = models.ForeignKey(
        SectionEvent,
        verbose_name=_("Мероприятие"),
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        Student,
        verbose_name=_("Участник"),
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Участник мероприятия")
        verbose_name_plural = _("Участники мероприятия")
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"


class SectionTraining(models.Model):
    section = models.ForeignKey(
        Section,
        verbose_name=_("Секция"),
        related_name="trainings",
        on_delete=models.CASCADE
    )
    members = models.ManyToManyField(
        Student,
        verbose_name="Участники",
        through="TrainingMember",
        related_name="trainings"
    )
    duration = models.IntegerField(
        verbose_name=_("Продолжительность"),
        default=0,
        help_text="Продолжительность тренировки в минутах"
    )
    datetime = models.DateTimeField(verbose_name=_("Дата проведения"))
    place = models.TextField(verbose_name=_("Место проведения"))
    is_active = models.BooleanField(verbose_name=_("Активна?"), default=True)

    class Meta:
        verbose_name = _("Тренировка")
        verbose_name_plural = _("Тренировки")


class TrainingMember(models.Model):
    training = models.ForeignKey(
        SectionTraining,
        verbose_name=_("Тренировка"),
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        Student,
        verbose_name=_("Участник"),
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Участник тренировки")
        verbose_name_plural = _("Участники тренировки")
        unique_together = ['training', 'user']

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"
