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
    SectionEvent
)
from .serializers import (
    UserSerializer,
    StudentSerializer, TrainerSerializer,
    SectionSerializer, SectionMemberSerializer,
    SectionEventSerializer
)


def init_user(request):
    """
        Получение пользователя по токену
    """
    user_id = Token.objects.get(key=request.headers.get("Authorization").replace("Token ", "")).user_id
    try:
        user = User.objects.get(id=user_id)
        user.set_rang()
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

