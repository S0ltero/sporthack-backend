from django.db import models


class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_trainer=False)


class TrainerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_trainer=True)