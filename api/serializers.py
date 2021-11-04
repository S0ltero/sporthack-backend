from djoser.serializers import PasswordRetypeSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token
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
            "id", "last_name", "first_name", "middle_name",
            "email", "phone", "institution", 
            "group", "photo", "rank"
        )
        extra_kwargs = {
            'email': {'required': False},
        }


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = (
            "id", "last_name", "first_name", "middle_name",
            "email", "photo", "institution", "group", "rating",
            "is_trainer"
        )


class TrainerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trainer
        fields = (
            "id", "last_name", "first_name", "middle_name",
            "email", "phone", "rank", "photo", "is_trainer"
        )


class TrainingMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainingMember
        fields = "__all__"


class SectionTrainingSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = SectionTraining
        fields = "__all__"

    def get_members(self, obj):
        return [StudentSerializer(m.user).data for m in obj.member.all()]


class SectionMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = SectionMember
        fields = "__all__"


class EventMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventMember
        fields = "__all__"


class SectionEventSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = SectionEvent
        fields = "__all__"
    
    def get_members(self, obj):
        return [StudentSerializer(m.user).data for m in obj.member.all()]


class SectionSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    trainers = TrainerSerializer(many=True, read_only=True)
    trainings = SectionTrainingSerializer(many=True, source="training")
    events = SectionEventSerializer(many=True, source="event")

    class Meta:
        model = Section
        fields = "__all__"

    def get_members(self, obj):
        return [StudentSerializer(m.user).data for m in obj.member.all()]

class StudentDetailSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()
    events = EventMemberSerializer(many=True, read_only=True, source="event")
    pass_trainings_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            "id", "last_name", "first_name", "middle_name",
            "email", "photo", "institution", "group", "is_trainer",
            "sections", "trainings", "events", "rating", 
            "pass_trainings_count"
        )

    def get_pass_trainings_count(self, obj):
        return obj.training.filter(training__is_active=False).count()

    def get_sections(self, obj):
        queryset = Section.objects.filter(id__in=obj.section.values_list("section"))
        sections = [{
            "id": section.id,
            "title": section.title,
            "count_members": SectionMember.objects.filter(section=section).count()
        } for section in queryset]
        return sections

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


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source="key")
    id = serializers.IntegerField(source="user.id")

    class Meta:
        model = Token
        fields = ("auth_token", "id")
