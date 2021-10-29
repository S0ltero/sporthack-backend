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
        fields = (
            "id", "username", "email",
            "phone", "institution", "group",
            "image", "rank"
        )
        extra_kwargs = {"username": {"required": False}}


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


class TrainingMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainingMember
        fields = "__all__"


class SectionTrainingSerializer(serializers.ModelSerializer):
    members = TrainingMemberSerializer(many=True, read_only=True)

    class Meta:
        model = SectionTraining
        fields = "__all__"


class EmailAndCodeSerializer(serializers.Serializer):

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        try:
            self.code = ResetPassCode.objects.get(
                user__email=self.initial_data.get("email", ""),
                code=int(self.initial_data.get("code", ""))
            )
        except (ResetPassCode.DoesNotExist, ValueError, TypeError, OverflowError):
            key_error = "invalid_code"
            raise ValidationError(code=key_error)
        
        self.user = User.objects.get(email=self.initial_data.get("email", ""))
        
        return validated_data


class PasswordResetConfirmSerializer(EmailAndCodeSerializer, PasswordRetypeSerializer):

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        self.code = ResetPassCode.objects.get(
            user__email=self.initial_data.get("email", ""),
            code=int(self.initial_data.get("code", ""))
        )
        self.code.delete()

        return validated_data