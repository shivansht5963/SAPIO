"""
URL configuration for FFMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from accounts.views import UserListView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('api/docs/', TemplateView.as_view(template_name='api_docs.html'), name='api-docs'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/', include('tasks.urls')),
    path('api/', include('visits.urls')),
    path('api/', include('activity_logs.urls')),
    path('api/', include('reports.urls')),
]

