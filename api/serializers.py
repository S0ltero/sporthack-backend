from djoser.serializers import PasswordRetypeSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    User, Student, Trainer, 
    Section, SectionMember, 
    SectionEvent, EventMember,
    SectionTraining, TrainingMember,
    ResetPassCode
)


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


class SectionMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = SectionMember
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    members = SectionMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = "__all__"


class EventMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventMember
        fields = "__all__"


class SectionEventSerializer(serializers.ModelSerializer):
    members = EventMemberSerializer(many=True, read_only=True)

    class Meta:
        model = SectionEvent
        fields = "__all__"

