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
    list_display = ("id", "username", "institution", "group", "is_active")
    list_filter = ("is_active",)
    list_display_links = ("username",)
    readonly_fields = ("sex", "password", "last_login", "date_joined")
    fieldsets = (
        ("Основная информация", {"fields": (("username", "email", "sex", "password"))}),
        ("Учебное заведение", {"fields": ("group", "institution")}),
        ("Дополнительная информация", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "fields": ("username", "email", "password1", "password2", "sex")}
         ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_trainer=False)
@admin.register(SectionEvent)
class AdminSectionEvent(admin.ModelAdmin):
    inlines = [EventMemberList]
    actions = None
