"""Market URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('user/create/', views.create_user),
    path('login/', views.auth_user),
    path('market/', views.market_commodity_list),
    path('commodity/have/', views.user_commodity_list),
    path('commodity/create/', views.create_commodity),
    path('commodity/up/', views.up_commodity),
    path('commodity/down/', views.down_commodity),
    path('transaction/', views.user_transaction_list),
    path('commodity/buy/', views.buy_commodity),
    path('arbitration/', views.initiate_arbitration),
]