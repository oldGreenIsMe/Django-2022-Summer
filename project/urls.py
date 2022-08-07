from django.urls import path
from .views import *

urlpatterns = {
    path('createProj', createProj),
    path('modifyProjPhoto', modifyProjPhoto),
    path('modifyProjInfo', modifyProjInfo),
    path('deleteProj', deleteProj),
    path('clearProj', clearProj),
    path('getDeletedProjList', getDeletedProjList),
    path('recover', recoverProj),
    path('detail', detailProj),
    path('create_proto', create_proto),
    path('upload_proto', upload_proto),
    path('upload_proto_photo', upload_proto_photo),
    path('get_proto', get_proto),
    path('rename_proto', rename_proto),
    path('delete_proto', delete_proto),
    path('proj_proto', proj_proto),
    path('createFile', createFile),
    path('deleteFile', deleteFile),
    path('modifyFile', modifyFile),
    path('renameFile', renameFile),
    path('getFileList', getFileList),
    path('getFileContent', getFileContent),
    path('edit_file', edit_file),
    path('upload_file_image', upload_file_image),
    path('file_center')
}
