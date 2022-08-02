from django.urls import path
from .views import *

urlpatterns = {
    path('rename', renameProj),
    path('detail', detailProj),
    path('createProj', createProj),
    path('deleteProj', deleteProj),
    path('clearProj', clearProj),
}
