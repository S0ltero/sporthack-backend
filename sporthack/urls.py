from django.contrib import admin
from django.urls import path, re_path, include

from api.views import LoginAPI
from knox import views as knox_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    re_path(r'auth/token/login/', LoginAPI.as_view(), name="login"),
    re_path(r'auth/token/logout', knox_views.LogoutView.as_view(), name='logout'),
    re_path(r'auth/toke/logoutall', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path("api/", include("api.urls")),
]

handler404 = "api.views.handler404"

