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
    path('recover', recoverProj)
}
