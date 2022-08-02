from django.urls import path
from .views import *

urlpatterns = {
    path('rename', renameProj),
    path('detail', detailProj),
    path('createProj', createProj),
    path('modifyPhoto', modifyPhoto),
    path('deleteProj', deleteProj),
    path('clearProj', clearProj),
    path('recover', recoverProj)
}
