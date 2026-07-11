from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_home, name='dashboard_home'),
    path('upload-csv/', views.upload_csv_view, name='upload_csv'),
    path('clear-history/', views.clear_history_view, name='clear_history'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
