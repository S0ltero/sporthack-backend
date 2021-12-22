import base64

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField, Base64FieldMixin

from .models import (
    User,
    Student,
    Trainer,
    StudentAward,
    Section,
    SectionMember,
    SectionEvent,
    EventMember,
    SectionTraining,
    TrainingMember
)


class CustomBase64ImageField(Base64ImageField):
    def to_representation(self, file):
        if self.represent_in_base64:
            if not file:
                return ""

            try:
                with open(file.path, "rb") as f:
                    extenstion = file.file.name.split(".")[-1]
                    base64_str = base64.b64encode(f.read()).decode()
                    return f"data:image/{extenstion};base64,{base64_str}"
            except Exception:
                raise IOError("Error encoding file")
        else:
            return super(Base64FieldMixin, self).to_representation(file)


class UserSerializer(serializers.ModelSerializer):
    photo = CustomBase64ImageField(represent_in_base64=True, required=False)

    class Meta:
        model = User
        fields = (
            "id", "last_name", "first_name", "middle_name",
            "email", "phone", "institution", 
            "group", "photo", "rank", "is_trainer"
        )


class StudentSerializer(serializers.ModelSerializer):
    photo = CustomBase64ImageField(represent_in_base64=True, required=False)

    class Meta:
        model = Student
        fields = (
            "id", "last_name", "first_name", "middle_name",
            "email", "photo", "institution", "group", "rating",
            "is_trainer"
        )


class StudentAwardSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentAward
        fields = "__all__"


class TrainerSerializer(serializers.ModelSerializer):
    photo = CustomBase64ImageField(represent_in_base64=True, required=False)
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Trainer
        fields = (
            "id", "last_name", "first_name", "middle_name",
            "email", "phone", "rank", "photo", "is_trainer",
            "sections"
        )

    def get_sections(self, obj):
        sections = []
        for section in obj.trainers.all():
            data = SectionSerializer(section).data
            data["count_members"] = section.member.count()
            sections.append(data)
        return sections


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


class SectionDetailSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    trainers = serializers.SerializerMethodField()
    trainings = serializers.SerializerMethodField()
    image = CustomBase64ImageField(represent_in_base64=True, required=False)

    class Meta:
        model = Section
        fields = "__all__"

    def get_members(self, obj):
        return [StudentSerializer(m.user).data for m in obj.member.all()]

    def get_trainers(self, obj):
        queryset = obj.trainers.all()
        trainers = TrainerSerializer(queryset, many=True)
        trainers = ({key: value for key, value in trainer.items() if key != "sections"} for trainer in trainers.data)
        return trainers
    
    def get_trainings(self, obj):
        queryset = obj.training.order_by("datetime")
        trainings = []
        for training in queryset:
            members = (StudentSerializer(m.user).data for m in obj.member.all())
            keys = ("id", "last_name", "first_name", "middle_name", "photo", "is_trainer")
            members = ({key: value for key, value in member.items() if key in keys} for member in members)
            trainings.append({
                "id": training.id,
                "datetime": timezone.make_naive(training.datetime),
                "place": training.place,
                "duration": training.duration,
                "is_active": training.is_active,
                "members": members
            })
        return trainings


class SectionSerializer(serializers.ModelSerializer):
    image = CustomBase64ImageField(represent_in_base64=True, required=False)

    class Meta:
        model = Section
        fields = ("id", "title", "image")


class StudentDetailSerializer(serializers.ModelSerializer):
    photo = CustomBase64ImageField(represent_in_base64=True, required=False)
    awards = serializers.SerializerMethodField()
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
            "pass_trainings_count", "awards"
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
            "datetime": timezone.make_naive(training.datetime).strftime("%H:%M")
        } for training in queryset]
        return trainings

    def get_awards(self, obj):
        queryset = obj.awards.filter(verified=True)
        serializer = StudentAwardSerializer(queryset, many=True)
        return serializer.data


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect Credentials Passed.')
