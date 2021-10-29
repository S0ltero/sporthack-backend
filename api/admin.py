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


@admin.register(SectionEvent)
class AdminSectionEvent(admin.ModelAdmin):
    inlines = [EventMemberList]
    actions = None
