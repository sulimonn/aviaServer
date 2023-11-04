from products.views import index
from .views import company_detail, control, company_titles
from django.urls import path

app_name = 'products'
urlpatterns = [
    path('', index, name='index'),
    path('company_detail/<slug:company_slug>/', company_detail, name='company_detail'),
    path('control/', control, name='control'),
    path('company/<int:company_id>/', company_titles, name='company_titles'),
]