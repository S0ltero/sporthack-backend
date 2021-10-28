from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core import validators
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser, UserManager):
    sex = models.CharField(verbose_name=_("Пол"), max_length=30)
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
    institution = models.TextField(verbose_name=_("Учебное заведение"), blank=True)
    group = models.CharField(verbose_name=_("Группа"), max_length=50, blank=True)
    rank = models.TextField(verbose_name=_("Звание"))
    phone = models.CharField(verbose_name=_("Номер телефона"), max_length=255)
    is_trainer = models.BooleanField(verbose_name=_("Тренер"), default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return f"(User: {self.id} - {self.username})"

