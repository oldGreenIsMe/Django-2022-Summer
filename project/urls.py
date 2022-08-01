from django.urls import path
from .views import *

urlpatterns = {
    path('createProj', createProj),
    path('deleteProj', deleteProj),
}
