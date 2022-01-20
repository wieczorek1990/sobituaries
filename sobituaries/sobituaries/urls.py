"""sobituaries URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.views.generic import base
from rest_framework import routers

from api import views


router = routers.DefaultRouter()

urlpatterns = [
    path('favicon.ico', base.RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
    path('admin/', admin.site.urls),
    path('api/cemetery-registers/',
         views.CemeteryRegisterListCreateView.as_view(),
         name='cemetery-registers'),
    path('api/cemetery-registers/<slug:slug>/',
         views.CemeteryRegisterRetrieveView.as_view(),
         name='cemetery-register-retrieve'),
    path('api/cemetery-registers/<slug:slug>/obituary-notices/',
         views.ObituaryNoticeListCreateView.as_view(),
         name='obituary-notices'),
    path('api/cemetery-registers/<slug:cemetery_register_slug>/obituary-notices/<slug:obituary_notice_slug>/',
         views.ObituaryNoticeTemplateView.as_view(),
         name='obituary-notice-retrieve'),
    path('api/cemetery-registers/<slug:cemetery_register_slug>/obituary-notices/<slug:obituary_notice_slug>/payments/',
         views.ObituaryNoticePaymentView.as_view(),
         name='obituary-notice-stripe-payment'),
    path('api/cemetery-registers/<slug:cemetery_register_slug>/obituary-notices/<slug:obituary_notice_slug>/payments/'
         'success/',
         views.ObituaryNoticePaymentSuccessView.as_view(),
         name='obituary-notice-stripe-payment-success'),
]
urlpatterns += router.urls
urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
