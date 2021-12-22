from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q

from .models import *


class SectionMemberList(admin.StackedInline):
    model = SectionMember
    extra = 0
    classes = ["collapse"]


class TrainingMemberList(admin.StackedInline):
    model = TrainingMember
    extra = 0
    classes = ["collapse"]


class EventMemberList(admin.StackedInline):
    model = EventMember
    extra = 0
    classes = ["collapse"]


class StudentAwardList(admin.StackedInline):
    model = StudentAward
    extra = 0
    classes = ["collapse"]


@admin.register(Student)
class AdminStudent(UserAdmin):
    actions = None
    inlines = [StudentAwardList]
    list_display = ("id", "last_name", "first_name", "middle_name", "institution", "group", "is_active")
    list_filter = ("is_active",)
    list_display_links = ("last_name", "first_name", "middle_name")
    readonly_fields = ("password", "last_login", "date_joined")
    fieldsets = (
        ("Основная информация", {"fields": ((("last_name", "first_name", "middle_name"), "photo", "email", "password"))}),
        ("Учебное заведение", {"fields": ("group", "institution")}),
        ("Дополнительная информация", {"fields": ("rating", "last_login", "date_joined")}),
    )
    add_fieldsets = (
        ("Личная информация", {
            "fields": (("last_name", "first_name", "middle_name"), "photo")}
         ),
        ("Учетная информация", {
             "fields": ("email", "password1", "password2")}
        )
    )
    ordering = ("last_name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_trainer=False, is_staff=False, is_superuser=False)


@admin.register(StudentAward)
class AdminStudentAward(admin.ModelAdmin):
    actions = None
    list_display = ("id", "user", "title", "category", "verified")
    list_filter = ("category", "verified")
    list_display_links = ("title",)
    fields = ("user", "title", "category", "file", "verified")
    ordering = ("verified",)


@admin.register(Trainer)
class AdminTrainer(UserAdmin):
    actions = None
    list_display = ("id", "last_name", "first_name", "middle_name", "phone", "is_active")
    list_filter = ("is_active",)
    list_display_links = ("last_name", "first_name", "middle_name")
    readonly_fields = ("password", "last_login", "date_joined")
    fieldsets = (
        ("Основная информация", {"fields": ((("last_name", "first_name", "middle_name"), "photo", "phone", "email", "password"))}),
        ("Дополнительная информация", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        ("Личная информация", {
            "fields": (("last_name", "first_name", "middle_name"), "photo", "phone", "rank")}
         ),
        ("Учетная информация", {
             "fields": ("email", "password1", "password2")}
        )
    )
    ordering = ("last_name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_trainer=True, is_staff=False, is_superuser=False)


@admin.register(Admin)
class AdminAdministrator(UserAdmin):
    actions = None
    list_display = ("id", "last_name", "first_name", "middle_name", "is_staff", "is_superuser",)
    list_filter = ("is_staff", "is_superuser")
    list_display_links = ("last_name", "first_name", "middle_name")
    readonly_fields = ("password", "last_login", "date_joined")
    fieldsets = (
        ("Основная информация", {"fields": ((("last_name", "first_name", "middle_name"), "email", "password"))}),
        ("Дополнительная информация", {"fields": ("is_staff", "is_superuser", "last_login", "date_joined")}),
    )
    add_fieldsets = (
        ("Личная информация", {
            "fields": (("last_name", "first_name", "middle_name"), "photo", "phone", "rank")}
         ),
        ("Учетная информация", {
             "fields": ("email", "password1", "password2")}
        )
    )
    ordering = ("last_name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(Q(is_staff=True) | Q(is_superuser=True))


@admin.register(Section)
class AdminSection(admin.ModelAdmin):
    inlines = [SectionMemberList]
    list_display = ("id", "title", "get_trainer")
    list_display_links = ("id", "title")

    @admin.display(description="Тренер")
    def get_trainer(self, obj):
        trainer = obj.trainers.first()
        return f"{trainer.last_name} {trainer.first_name} {trainer.middle_name}"

    actions = None


@admin.register(SectionTraining)
class AdminSectionTraining(admin.ModelAdmin):
    inlines = [TrainingMemberList]
    list_display = ("id", "section", "datetime", "place", "duration", "is_active")
    list_display_links = ("id", "section")
    list_filter = ("is_active", "datetime")
    fields = ("section", "datetime", "place", "duration")
    actions = None


@admin.register(SectionEvent)
class AdminSectionEvent(admin.ModelAdmin):
    inlines = [EventMemberList]
    list_display = ("id", "title", "level", "datetime", "place", "is_active")
    list_display_links = ("id", "title")
    list_filter = ("is_active", "datetime")
    fields = ("section", "title", "level", "datetime", "place")
    actions = None
