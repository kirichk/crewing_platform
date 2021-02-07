from django.urls import path
from django.conf import settings
from vbbot import views

app_name = 'vbbot'
token = settings.VIBER_TOKEN

urlpatterns = [
    path(token, views.viber_app),
    ]
