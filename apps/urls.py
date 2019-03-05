from django.urls import path
from apps import views

app_name = 'apps'
urlpatterns = [
    path('ketik/', views.ketik),
    path('unggah/', views.unggah),
    path('unggah/file/', views.file),
    path('ketik/ketik/', views.ketik),
]