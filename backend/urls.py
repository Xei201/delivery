from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/', include('api.urls')),
]
