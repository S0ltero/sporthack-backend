from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager
from django.db.models import Q


class StudentManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_trainer=False)


class TrainerManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_trainer=True)


class AdminManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(Q(is_staff=True) | Q(is_superuser=True))
