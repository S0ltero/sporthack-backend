from djoser.serializers import PasswordRetypeSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (User, Student, Trainer, Section, 
                     SectionMember, ResetPassCode)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        exclude = ("phone", "rank")


class TrainerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trainer
        exclude = ("institution", "group")

