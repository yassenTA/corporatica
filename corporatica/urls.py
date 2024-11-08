"""
URL configuration for corporatica project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Your API",
      default_version='v1',
      description="API for image processing",
      terms_of_service="https://www.yourapi.com/terms/",
      contact=openapi.Contact(email="yassentamer701@gmail.com", name="Yassen Tamer"),
      license=openapi.License(name="YTA"),
   ),
   public=True,
)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("user.api.urls")),
    path("api/", include("tabular.api.urls")),
    path("api/", include("image_processing.api.urls")),
    path("api/", include("text_analysis.api.urls")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path(
        "redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc-ui"
    ),
    # Add your other URL patterns here
]
