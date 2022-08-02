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
    # http://127.0.0.1/api/team/invite_user
    path('invite_user', invite_user),
    # http://127.0.0.1/api/team/delete_member
    path('delete_member', delete_member),
    # http://127.0.0.1/api/team/userspace
    path('userspace', userspace)
}
