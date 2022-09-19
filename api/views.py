import pytz
from datetime import datetime

from django.contrib.auth import login
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponseRedirect, HttpResponseNotFound
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    GenericAPIView
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import HTTP_HEADER_ENCODING
from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication

from .models import (
    User, 
    Student, Trainer, StudentAward,
    Section, SectionMember,
    SectionEvent, EventMember,
    SectionTraining, TrainingMember,
)
from .serializers import (
    UserSerializer, StudentSerializer,
    StudentDetailSerializer, StudentAwardSerializer,
    TrainerDetailSerializer, SectionSerializer, SectionDetailSerializer,
    SectionMemberSerializer, SectionEventSerializer,
    EventMemberSerializer, SectionTrainingSerializer, 
    TrainingMemberSerializer, LoginSerializer
)
from .permissions import IsTrainer


class UserView(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = User
    serializer_class = UserSerializer

    def update(self, request):
        serializer = self.serializer_class(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.update(request.user, serializer.validated_data)
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


class StudentAwardCreateView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = StudentAward
    serializer_class = StudentAwardSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


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
    serializer_class = TrainerDetailSerializer

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
            sections = self.queryset.objects.all().only('id', 'title')
        except Section.DoesNotExist:
            return Response(data={"description": f"Секции не найдены", "error": "sections_not_found"}, status=404)

        serializer = self.serializer_class(sections, many=True)
        return Response(serializer.data, status=200)


class SectionDetailListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Section
    serializer_class = SectionDetailSerializer

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
    serializer_class = SectionDetailSerializer

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
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = SectionMember
    serializer_class = SectionMemberSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id
        serializer = self.serializer_class(data=data)
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
            return Response(status=200)
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
    authentication_classes = (TokenAuthentication,)
    queryset = TrainingMember
    serializer_class = TrainingMemberSerializer

    def get(self, request, pk):
        token = request.COOKIES.get('token')
        if not token:
           return HttpResponseRedirect(redirect_to="/login") 
        token = token.encode(HTTP_HEADER_ENCODING)
        user, token = TokenAuthentication().authenticate_credentials(token=token)
        if not user:
            return HttpResponseRedirect(redirect_to="/login")
        request.data["user"] = user.id
        try:
            training = SectionTraining.objects.get(id=pk)
            request.data["training"] = training.id
        except SectionTraining.DoesNotExist:
            return HttpResponseRedirect(redirect_to="/profile")
        if training.datetime < timezone.now():
            timedelta = timezone.now() - training.datetime
            diff_hours = timedelta.total_seconds() // 60 // 60
            if diff_hours >= 3:
                return HttpResponseRedirect(redirect_to="/profile")
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return HttpResponseRedirect(redirect_to="/profile")
        else:
            return HttpResponseRedirect(redirect_to="/profile")


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
                    events = events.order_by('datetime')
            serializer = self.serializer_class(events, many=True)
            return Response(serializer.data, status=200)
        except SectionEvent.DoesNotExist:
            return Response(
                data={"desctiption": "Мероприятия не найдены", 
                      "error": "events_not_found"},
                status=404)


class EventMemberCreateView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = EventMember
    serializer_class = EventMemberSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user
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
        serializer = self.serializer_class(data=data)
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


class LoginAPI(KnoxLoginView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        return super(LoginAPI, self).post(request)

    def get_post_response_data(self, request, token, instance):
        UserSerializer = self.get_user_serializer_class()

        data = {
            "expiry": self.format_expiry_datetime(instance.expiry),
            "auth_token": token
        }
        if UserSerializer is not None:
            user = UserSerializer(
                request.user,
                context=self.get_context()
            ).data
            data["id"] = user["id"]
            data["is_trainer"] = user["is_trainer"]
        return data


def handler404(request, exception):
    template = get_template("error/404.html")
    return HttpResponseNotFound(template.render())
