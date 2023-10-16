from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from products.views import index


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', index, name='index'),
    path('products/', include('products.urls', namespace='products')),
    path('users/', include('users.urls', namespace='users')),
    path('oversight/', include('supervision.urls', namespace='supervision')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

