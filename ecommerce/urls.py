"""ecommerce URL Configuration

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
from django.urls import path, include
from ecommerce import settings
from django.conf.urls.static import static
from home.views import homeView, searchView
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from home import views as core_views

urlpatterns = [
    path('firsatlar/', include("campaings.urls")),  # < --- Campaign Urls
    path('blog/', include("blog.urls")),  # < --- Blog Urls
    path('hakkimizda', core_views.hakkimizda, name="hakkimizda"),  # < --- Hakkimizda Url
    path('sss', core_views.sss, name="sss"),  # < --- Hakkimizda Url

    url('^', include('django.contrib.auth.urls')),
    url(r'^password_reset/$', auth_views.PasswordResetView),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView),

    url(r'^oauth/', include('social_django.urls', namespace='social')),  # <-- for social media auth

    path('admin/', admin.site.urls),
    path('kullanici/', include('account.urls')),  # Account Urls
    path('ara/', searchView, name="searchView"),
    path('home/', include('home.urls')),

    path('', homeView, name="homeView"),
    path('', include('product.urls')),  # Product And Category urls
    path('chaining/', include('smart_selects.urls')),  # Django Smart Select
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
