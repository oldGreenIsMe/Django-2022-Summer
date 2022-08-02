from django.urls import path
from .views import *

urlpatterns = {
    # http://127.0.0.1/api/team/login
    path('login', login),
    # http://127.0.0.1/api/team/register
    path('register', register),
    # http://127.0.0.1/api/team/create_team
    path('create_team', create_team),
    # http://127.0.0.1/api/team/authorize_admin
    path('authorize_admin', authorize_admin),
    # http://127.0.0.1/api/team/invite_admin
    path('invite_admin', invite_admin),
}
