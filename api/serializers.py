from djoser.serializers import PasswordRetypeSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (User, Student, Trainer, Section, 
                     SectionMember, ResetPassCode)


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        exclude = ("phone", "rank")

