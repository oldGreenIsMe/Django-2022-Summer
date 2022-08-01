from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/team/', include(('team.urls', 'team'))),
    path('api/project/', include(('project.urls', 'project'))),
]
