from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/health', views.uptime_view),
    path('v1/ov/submissions/', views.submissions),
    path('v1/ov/submissions/<int:cislo_id>', views.vymaz),
    path('v1/companies/', views.companies),
]