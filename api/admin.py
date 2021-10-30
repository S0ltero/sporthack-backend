from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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


@admin.register(Student)
class AdminStudent(UserAdmin):
    actions = None
    list_display = ("id", "last_name", "first_name", "middle_name", "institution", "group", "is_active")
    list_filter = ("is_active",)
    list_display_links = ("last_name", "first_name", "middle_name")
    readonly_fields = ("password", "last_login", "date_joined")
    fieldsets = (
        ("Основная информация", {"fields": (("first_name", "last_name", "middle_name", "email", "sex", "password"))}),
        ("Учебное заведение", {"fields": ("group", "institution")}),
        ("Дополнительная информация", {"fields": ("rating", "last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "fields": ("last_name", "first_name", "middle_name", "sex", "email", "password1", "password2")}
         ),
    )
    ordering = ("last_name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_trainer=False)


@admin.register(Trainer)
class AdminTrainer(UserAdmin):
    actions = None
    list_display = ("id", "last_name", "first_name", "middle_name", "phone", "is_active")
    list_filter = ("is_active",)
    list_display_links = ("last_name", "first_name", "middle_name")
    readonly_fields = ("password", "last_login", "date_joined")
    fieldsets = (
        ("Основная информация", {"fields": ((("last_name", "first_name", "middle_name",), "email", "sex", "password"))}),
        ("Дополнительная информация", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "fields": (("last_name","first_name", "middle_name",), "sex", "email", "password1", "password2")}
         ),
    )
    ordering = ("last_name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_trainer=True)


@admin.register(Section)
class AdminSection(admin.ModelAdmin):
    inlines = [SectionMemberList]
    list_display = ("id", "title")
    list_display_links = ("id", "title")
    actions = None


@admin.register(SectionTraining)
class AdminSectionTraining(admin.ModelAdmin):
    inlines = [TrainingMemberList]
    list_display = ("id", "section", "datetime", "duration", "is_active")
    list_display_links = ("id", "section")
    list_filter = ("is_active", "datetime")
    actions = None


@admin.register(SectionEvent)
class AdminSectionEvent(admin.ModelAdmin):
    inlines = [EventMemberList]
    list_display = ("id", "title", "level", "datetime", "place", "is_active")
    list_display_links = ("id", "title")
    list_filter = ("is_active", "datetime")
    actions = None
