from django.urls import path 
from api import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'), 
    path('home', views.home, name='home'),  
    path('about', views.about, name='about'),
    path('detection', views.detection, name='detection'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)