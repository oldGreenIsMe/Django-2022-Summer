from django.urls import path
from .views import *

urlpatterns = {
    # http://127.0.0.1/api/team/login
    path('login', login),
    # http://127.0.0.1/api/team/register
    path('register', register),
}
