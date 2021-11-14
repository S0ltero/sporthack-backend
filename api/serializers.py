from djoser.serializers import PasswordRetypeSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField

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
    section_ids = serializers.SerializerMethodField()
    section_titles = serializers.SerializerMethodField()

    class Meta:
        model = Trainer
        fields = (
            "id", "last_name", "first_name", "middle_name",
            "email", "phone", "rank", "photo", "is_trainer",
            "section_ids", "section_titles"
        )

    def get_section_ids(self, obj):
        return obj.trainers.values_list("id", flat=True)

    def get_section_titles(self, obj):
        return obj.trainers.values_list("title", flat=True)


class TrainingMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainingMember
        fields = "__all__"


class SectionTrainingSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    datetime = serializers.DateTimeField(format="%d-%m-%Y %H:%M")

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
    trainings = serializers.SerializerMethodField()
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
            "count_members": section.member.count(),
            "rating": section.member.get(user=obj).rating,
            "pass_trainings_count": section.member.get(user=obj).pass_trainings
        } for section in queryset]
        return sections
    
    def get_trainings(self, obj):
        queryset = SectionTraining.objects.filter(section__in=obj.section.values_list("section"), is_active=True)
        trainings = [{
            "id": training.id,
            "place": training.place,
            "datetime": training.datetime.strftime("%H:%M")
        } for training in queryset]
        return trainings


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source="key")
    id = serializers.IntegerField(source="user.id")
    is_trainer = serializers.BooleanField(source="user.is_trainer")

    class Meta:
        model = Token
        fields = ("auth_token", "id", "is_trainer")
