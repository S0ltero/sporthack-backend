from django.db import models
from django.contrib.auth.models import BaseUserManager


class StudentManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_trainer=False)


class TrainerManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_trainer=True)