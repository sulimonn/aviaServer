from products.views import index
from .views import company_detail, control, point, company_titles, grant_access, update_perm
from django.urls import path
from . import views

app_name = 'products'
urlpatterns = [
    path('', index, name='index'),
    path('company_detail/<slug:company_slug>/', company_detail, name='company_detail'),
    path('control/', control, name='control'),
    path('<slug:user_slug>/point/', point, name='point'),
    path('company/<int:company_id>/', company_titles, name='company_titles'),
    path('grant_access/<slug:user_slug>/', grant_access, name='grant_access'),
    path('update-permission/<slug:user_slug>/', update_perm, name='update_perm'),
]