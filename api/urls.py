from django.urls import path

from .views import *

urlpatterns = [
    path("user/edit", UserView.as_view(), name="user-edit"),
    path("users/trainer/<int:pk>", TrainerView.as_view(), name="user-trainer"),
    path("users/student/<int:pk>", StudentView.as_view(), name="user-student"),
    path("users/student-detail/<int:pk>", StudentDetailView.as_view(), name="user-student-detail"),
    path("rating/", StudentRatingListView.as_view(), name="rating"),

    path("sections/", SectionDetailListView.as_view(), name="sections"),
    path("sections-compress/", SectionListView.as_view(), name="sections-compress"),
    path("section/<int:pk>", SectionView.as_view(), name="section"),
    path("section/create-member", SectionMemberCreateView.as_view(), name="create-section-member"),
    path("section/delete-member", SectionMemberDeleteView.as_view(), name="delete-section-member"),

    path("trainings/<int:pk>", SectionTrainingListView.as_view(), name="trainings"),
    path("trainings-date/", SectionTrainingListView.as_view(), name="training-date"),
    path("training/create-member/<int:pk>", TrainingMemberCreateView.as_view(), name="create-training-member"),
    path("training/delete-member/<int:pk>", TrainingMemberDeleteView.as_view(), name="delete-training-member"),

    path("events/", SectionEventListView.as_view(), name="events"),
    path("event/create-member", EventMemberCreateView.as_view(), name="create-event-member"),
    path("event/delete-member", EventMemberDeleteView.as_view(), name="delete-event-member")
]
