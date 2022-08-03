from django.urls import path
from .views import *

urlpatterns = {
    path('rename', renameProj),
    path('detail', detailProj),
    path('createProj', createProj),
    path('modifyPhoto', modifyPhoto),
    path('deleteProj', deleteProj),
    path('clearProj', clearProj),
    path('recover', recoverProj),
    path('create_proto', create_proto),
    path('upload_proto', upload_proto),
    path('get_proto', get_proto),
    path('rename_proto', rename_proto)
}
