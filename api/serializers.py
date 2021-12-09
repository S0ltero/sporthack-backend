import base64

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from drf_extra_fields.fields import Base64ImageField

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


def convert_image_to_base64(image) -> str:
    with open(image.path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()
    image_ext = image.file.name.split(".")[-1]
    return f"data:image/{image_ext};base64,{image_base64}"


class UserSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(represent_in_base64=True, required=False)

    class Meta:
        model = User
        fields = (
            "id", "last_name", "first_name", "middle_name",
            "sex", "email", "phone", "institution", 
            "group", "photo", "rank", "is_trainer"
        )
        extra_kwargs = {
            'email': {'required': False},
        }

    def to_representation(self, instance):
        image = instance.photo
        data = super().to_representation(instance)
        data['photo'] = convert_image_to_base64(image)
        return data


class StudentSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(represent_in_base64=True, required=False)

    class Meta:
        model = Student
        fields = (
            "id", "last_name", "first_name", "middle_name",
            "email", "photo", "institution", "group", "rating",
            "is_trainer"
        )

    def to_representation(self, instance):
        image = instance.photo
        data = super().to_representation(instance)
        data['photo'] = convert_image_to_base64(image)
        return data


class StudentAwardSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentAward
        fields = "__all__"


class TrainerSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(represent_in_base64=True, required=False)
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Trainer
        fields = (
            "id", "last_name", "first_name", "middle_name",
            "email", "phone", "rank", "photo", "is_trainer",
            "sections"
        )

    def get_sections(self, obj):
        sections = [{
            "id": section.id,
            "title": section.title,
            "image": convert_image_to_base64(section.image),
            "count_members": section.member.count()
        } for section in obj.trainers.all()]
        return sections
    
    def to_representation(self, instance):
        image = instance.photo
        data = super().to_representation(instance)
        data['photo'] = convert_image_to_base64(image)
        return data


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
    image = Base64ImageField(represent_in_base64=True, required=False)

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
        queryset = obj.training.all()
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
        trainings = sorted(trainings, key=lambda x: x["datetime"])
        return trainings

    def to_representation(self, instance):
        image = instance.image
        data = super().to_representation(instance)
        data['image'] = convert_image_to_base64(image)
        return data


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ("id", "title", "image")
    
    def to_representation(self, instance):
        image = instance.image
        data = super().to_representation(instance)
        data['image'] = convert_image_to_base64(image)
        return data


class StudentDetailSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(represent_in_base64=True, required=False)
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
            "datetime": timezone.make_naive(training.datetime).strftime("%H:%M")
        } for training in queryset]
        return trainings

    def to_representation(self, instance):
        image = instance.photo
        data = super().to_representation(instance)
        data['photo'] = convert_image_to_base64(image)
        return data


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source="key")
    id = serializers.IntegerField(source="user.id")
    is_trainer = serializers.BooleanField(source="user.is_trainer")

    class Meta:
        model = Token
        fields = ("auth_token", "id", "is_trainer")


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