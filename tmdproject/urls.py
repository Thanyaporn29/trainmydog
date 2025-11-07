from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ระบบสมาชิก (login/register/profile)
    path('auth/', include(('base.urls', 'base'), namespace='Authen')),

    # หน้าแรกและหน้าเว็บทั้งหมด
    path('', include(('trainmydog.urls', 'trainmydog'), namespace='trainmydog')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
