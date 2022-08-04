from django.urls import path
from .views import *

urlpatterns = {
    path('rename', renameProj),
    path('detail', detailProj),
    path('createProj', createProj),
    path('modifyProjPhoto', modifyProjPhoto),
    path('modifyProjInfo', modifyProjInfo),
    path('deleteProj', deleteProj),
    path('clearProj', clearProj),
    path('getDeletedProjList', getDeletedProjList),
    path('recover', recoverProj),
    path('create_proto', create_proto),
    path('upload_proto', upload_proto),
    path('get_proto', get_proto),
    path('rename_proto', rename_proto),
    path('delete_proto', delete_proto),
    path('createFile', createFile),
    path('deleteFile', deleteFile),
    path('modifyFile', modifyFile),
    path('renameFile', renameFile),
    path('getFileList', getFileList),
    path('getFileContent', getFileContent),
}
