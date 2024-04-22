from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from products.views import index
from django.urls import path, include

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', index, name='index'),
    path('', include('products.urls', namespace='products')),
    path('oversight/', include('supervision.urls', namespace='supervision')),
    path('users/', include('users.urls', namespace='users')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

