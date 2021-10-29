from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import (
    User, 
    Student, Trainer, 
    Section, SectionMember,
    SectionEvent, EventMember,
    SectionTraining, TrainingMember,
    ResetPassCode
)
from .serializers import (
    UserSerializer,
    StudentSerializer, TrainerSerializer,
    SectionSerializer, SectionMemberSerializer,
    SectionEventSerializer, EventMemberSerializer,
    SectionTrainingSerializer, TrainingMemberSerializer,
)


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
            student = self.queryset.get(id=pk)
        except Trainer.DoesNotExist:
            return Response(data={"description": f"Студент: {pk} не найден!", "error": "student_not_found"})
        serializer = self.serializer_class(student)
        return Response(serializer.data, status=200)


class TrainerView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Trainer
    serializer_class = TrainerSerializer

    def retrieve(self, request, pk):
        try:
            trainer = self.queryset.get(id=pk)
        except Trainer.DoesNotExist:
            return Response(data={"description": f"Тренер: {pk} не найден!", "error": "trainer_not_found"}, status=404)
        serializer = self.serializer_class(trainer)
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
            return Response(data={"desctiption": "Мероприятия не найдены", "error": "events_not_found"})


class SectionMemberCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SectionMember
    serializer_class = SectionMemberSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)
