from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_principala, name='home'),
    path('compare/', views.compara_orase, name='compare'),
]