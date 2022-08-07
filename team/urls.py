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
    path('userspace', userspace),
    # http://127.0.0.1/api/team/teamspace
    path('teamspace', teamspace),
    # http://127.0.0.1/api/team/team_manage
    path('team_manage', team_manage),
    path('modify_username', modify_username),
    path('modify_password', modify_password),
    path('modify_photo', modify_photo),
    path('delete_team', delete_team),
    path('handleInvitation', handleInvitation),
    path('search_team', search_team),
    path('apply_join', apply_join),
    path('search_user', search_user),
    path('sendVerifyCode', sendVerifyCode),
    path('acceptInvitation', acceptInvitation),
}
