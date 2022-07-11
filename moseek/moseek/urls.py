from django.contrib import admin
from django.urls import path
from chart import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('create/', views.create, name='create'),
    path('example/', views.example, name='example'),
]
