"""tech_preview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, re_path, include
from tech_blogs_app.views import *
from django.contrib.auth import login, logout
from django.views.generic.base import RedirectView


favicon_view = RedirectView.as_view(url='/static/favicon.ico')

urlpatterns = [
    # Стандартный набор - админка, вход и выход для пользователя, заглушка
    re_path(r'favicon\.ico$', favicon_view),
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),

    # Получить либо свой блог - без указания SLUG, либо чужого пользователя.
    path('other/<slug:slug>', BlogListSelfView.as_view(), name='blog'),
    # Не оговорено в ТЗ, но тогда не вижу способа подписываться на чужие посты
    path('', BlogListSelfView.as_view(), name='self_blog'),
    
    path('detail/<int:pk>', BlogDetailView.as_view(), name='blog_detail'),
    # Новостная лента текущего пользователя
    path('news/', NewsListView.as_view(), name='feed'),
    # Не получилось засунуть JSON запрос в ClassBased View
    path('api.main/read/get', get_read, name='get_read')
]
