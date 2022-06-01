from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/health', views.uptime_view),
    path('v1/ov/submissions/', views.submissions),
    path('v1/ov/submissions/<int:cislo_id>', views.vymaz),
    path('v1/companies/', views.companies),
    path('v2/ov/submissions/', views.v2_submissions),
    path('v2/ov/submissions/<int:cislo_id>', views.v2_ziskaj_vymaz),
    path('v2/companies/', views.v2_companies),
]