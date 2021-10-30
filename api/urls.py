from django.urls import path

from .views import *

urlpatterns = [
    path("user/edit", UserView.as_view(), name="user-edit"),
    path("users/trainer/<int:pk>", TrainerView.as_view(), name="user-trainer"),
    path("users/student/<int:pk>", StudentView.as_view(), name="user-student"),
    path("reset-password/", ResetPasswordView.as_view(), name='reset-password'),

    path("sections/", SectionListView.as_view(), name="sections"),
    path("section/<int:pk>", SectionView.as_view(), name="section"),
    path("section/create-member", SectionMemberCreateView.as_view(), name="create-section-member"),
    path("section/delete-member", SectionMemberDeleteView.as_view(), name="delete-section-member"),

    path("training/create-member", TrainingMemberCreateView.as_view(), name="create-training-member"),
    path("training/delete-member", TrainingMemberDeleteView.as_view(), name="delete-training-member"),

    path("events/", SectionEventListView.as_view(), name="events"),
    path("event/create-member", EventMemberCreateView.as_view(), name="create-event-member"),
    path("event/delete-member", EventMemberDeleteView.as_view(), name="delete-event-member")
]