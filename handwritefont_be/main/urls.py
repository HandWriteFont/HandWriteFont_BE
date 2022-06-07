"""handwritefont_be URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from .views import FontListView, FontView, fontview, NameUniqueCheck

urlpatterns = [
    path('', FontListView.as_view()),
    path('name-check/', NameUniqueCheck.as_view()),
    path('<str:pk>/', FontView.as_view()),
    path('lookaround',fontview ),
]