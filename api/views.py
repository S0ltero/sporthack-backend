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
