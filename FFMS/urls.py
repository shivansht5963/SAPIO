"""
URL configuration for FFMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('tasks.urls')),
    path('api/', include('visits.urls')),
    path('api/', include('activity_logs.urls')),
]
