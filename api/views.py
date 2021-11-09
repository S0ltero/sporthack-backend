import random
import pytz
from datetime import datetime

from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    GenericAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser

from .models import (
    User, 
    Student, Trainer, 
    Section, SectionMember,
    SectionEvent, EventMember,
    SectionTraining, TrainingMember,
    ResetPassCode
)
from .serializers import (
    UserSerializer, StudentSerializer,
    StudentDetailSerializer, TrainerSerializer,
    SectionSerializer, SectionMemberSerializer,
    SectionEventSerializer, EventMemberSerializer,
    SectionTrainingSerializer, TrainingMemberSerializer,
   
)
from .permissions import IsTrainer


def init_user(request):
    """
        Получение пользователя по токену
    """
    user_id = Token.objects.get(key=request.headers.get("Authorization").replace("Token ", "")).user_id
    try:
        user = User.objects.get(id=user_id)
        return user
    except User.DoesNotExist:
        return None


class UserView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser,)

    def update(self, request):
        user = init_user(request)
        serializer = self.serializer_class(instance=user, data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.update(user, serializer.validated_data)
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)


class StudentView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Student
    serializer_class = StudentSerializer

    def retrieve(self, request, pk):
        try:
            student = self.queryset.objects.get(id=pk)
        except Student.DoesNotExist:
            return Response(data={"description": f"Студент: {pk} не найден!", "error": "student_not_found"})
        serializer = self.serializer_class(student)
        return Response(serializer.data, status=200)


class StudentDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Student
    serializer_class = StudentDetailSerializer

    def retrieve(self, request, pk):
        try:
            student = self.queryset.objects.get(id=pk)
        except Student.DoesNotExist:
            return Response(data={"description": f"Студент: {pk} не найден!", "error": "student_not_found"})
        serializer = self.serializer_class(student)
        return Response(serializer.data, status=200)


class StudentRatingListView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Student
    serializer_class = StudentSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            students = self.queryset.objects.order_by("-rating")[:10]
        except Student.DoesNotExist:
            return Response(data={"description": "Студенты не найдены!", "error": "students_not_found"}, status=404)
        serializer = self.serializer_class(students, many=True)
        return Response(serializer.data, status=200)


class TrainerView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Trainer
    serializer_class = TrainerSerializer

    def retrieve(self, request, pk):
        try:
            trainer = self.queryset.objects.get(id=pk)
        except Trainer.DoesNotExist:
            return Response(data={"description": f"Тренер: {pk} не найден!", "error": "trainer_not_found"}, status=404)
        serializer = self.serializer_class(trainer)
        return Response(serializer.data, status=200)


class SectionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Section
    serializer_class = SectionSerializer

    def get(self, request, *args, **kwargs):
        try:
            sections = self.queryset.objects.all()
        except Section.DoesNotExist:
            return Response(data={"description": f"Секции не найдены", "error": "sections_not_found"}, status=404)
        
        serializer = self.serializer_class(sections, many=True)
        return Response(serializer.data, status=200)


class SectionView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Section
    serializer_class = SectionSerializer

    def retrieve(self, request, pk):
        try:
            section = self.queryset.objects.get(id=pk)
        except Section.DoesNotExist:
            return Response(data={"description": f"Секция: {pk} не найдена!", "error": "section_not_found"}, status=404)
        serializer = self.serializer_class(section)
        return Response(serializer.data, status=200)

    def update(self, request, pk):
        try:
            section = self.queryset.objects.get(id=pk)
        except Section.DoesNotExist:
            return Response(data={"description": f"Секция: {pk} не найдена!", "error": "section_not_found"}, status=404)
        serializer = self.serializer_class(section, data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.update(section, serializer.validated_data)
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)


class SectionMemberCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SectionMember
    serializer_class = SectionMemberSerializer

    def create(self, request, *args, **kwargs):
        request.data["user"] = init_user(request).id
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class SectionMemberDeleteView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsTrainer]
    queryset = SectionMember
    serializer_class = SectionMemberSerializer

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user")
        section_id = request.data.get("section")
        try:
            member = self.queryset.objects.get(section_id=section_id, user_id=user_id)
            member.delete()
        except SectionMember.DoesNotExist:
            return Response(
                data={"description": f"Участник: {user_id}, Секции {section_id} не найден!", 
                      "error": "section_member_not_found"}, 
                status=404)


class SectionTrainingListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SectionTraining
    serializer_class = SectionTrainingSerializer

    def get(self, request, pk):
        try:
            trainings = self.queryset.objects.filter(section=pk)
        except SectionTraining.DoesNotExist:
            return Response(
                data={"description": "Тренировки не найдены", 
                      "error": "trainings_not_found"}, 
                status=404)

        serializer = self.serializer_class(trainings, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        date = request.data.get("date")
        dt = datetime.strptime(date, "%Y-%m-%d")
        dt = dt.astimezone(pytz.timezone("Europe/Moscow"))
        try:
            trainings = self.queryset.objects.filter(datetime__date=dt.date())
        except SectionTraining.DoesNotExist:
            return Response(
                data={"description": "Тренировки не найдены", 
                      "error": "trainings_not_found"}, 
                status=404)

        serializer = self.serializer_class(trainings, many=True)
        return Response(serializer.data, status=200)

class SectionTrainingView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SectionTraining
    serializer_class = SectionTrainingSerializer

    def retrieve(self, request, pk):
        try:
            training = self.queryset.objects.get(id=pk)
        except SectionTraining.DoesNotExist:
            return Response(
                data={"description": f"Тренировка: {pk} не найдена",
                      "error": "training_not_found"}
            )
        serializer = self.serializer_class(training)
        return Response(serializer.data, status=200)


class TrainingMemberCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TrainingMember
    serializer_class = TrainingMemberSerializer

    def get(self, request, pk):
        request.data["user"] = init_user(request).id
        try:
            training = SectionTraining.objects.get(id=pk)
        except SectionTraining.DoesNotExist:
            return Response(
                data={"description": f"Тренировка: {pk} не найдена",
                      "error": "training_not_found"},
                status=404
            )
        if training.datetime < timezone.now():
            return Response(
                data={"description": "Невозможно добавление участника к прошедшей тренировке",
                      "error": "training_is_expired"},
                status=400
            )
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class TrainingMemberDeleteView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsTrainer]
    queryset = TrainingMember

    def get(self, request, pk):
        user_id = request.data.get("user")
        try:
            member = self.queryset.objects.get(training_id=pk, user_id=user_id)
            member.delete()
        except SectionMember.DoesNotExist:
            return Response(
                data={"description": f"Участник: {user_id}, Тренировки: {pk} не найден!", 
                      "error": "training_member_not_found"}, 
                status=404
            )


class SectionEventListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SectionEvent
    serializer_class = SectionEventSerializer

    def post(self, request, *args, **kwargs):
        try:
            events = self.queryset.objects.all()
            for key, value in request.data.items():
                if value:
                    events = events.filter(**{key: value})
            serializer = self.serializer_class(events, many=True)
            return Response(serializer.data, status=200)
        except SectionEvent.DoesNotExist:
            return Response(
                data={"desctiption": "Мероприятия не найдены", 
                      "error": "events_not_found"},
                status=404)


class EventMemberCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EventMember
    serializer_class = EventMemberSerializer

    def create(self, request, *args, **kwargs):
        request.data["user"] = init_user(request).id
        try:
            event = SectionTraining.objects.get(id=request.data.get("event"))
        except SectionTraining.DoesNotExist:
            return Response(
                data={"description": f"Мероприятие: {request.data.get('event')} не найдено",
                      "error": "event_not_found"},
                status=404
            )
        if event.datetime < timezone.now():
            return Response(
                data={"description": "Невозможно добавление участника к прошедшей тренировке",
                      "error": "event_is_expired"},
                status=400
            )
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class EventMemberDeleteView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsTrainer]
    queryset = EventMember
    serializer_class = EventMemberSerializer

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user")
        event_id = request.data.get("event")
        try:
            member = self.queryset.objects.get(event_id=event_id, user_id=user_id)
            member.delete()
        except SectionMember.DoesNotExist:
            return Response(
                data={"description": f"Участник: {user_id}, Мероприятия: {event_id} не найден!", 
                      "error": "event_member_not_found"}, 
                status=404
            )


class ResetPasswordView(CreateAPIView):

    def create(self, request):
        data = request.data

        try:
            user = User.objects.get(email=data.get("email"))
        except User.DoesNotExist as e:
            return Response(data={"description": f"{e}", "error": "user_not_found"}, status=404)

        if user.is_authenticated:
            return Response(data={'description': "Указанный пользователь аунтентифицирован", "error": "user_is_authenticated"}, status=400)

        code = random.randint(1000, 9999)
        ResetPassCode.objects.create(user=user, code=code)
        send_mail(f'SportHack | Сброс пароля', f'Ваш код для сброса пароля: {code}',  from_email="ecomap@gmail.com", recipient_list=[user.email])
        return Response(status=202)
