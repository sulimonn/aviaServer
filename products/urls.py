from products.views import index
from .views import  companies_list, create_company, edit_company
from django.urls import path

app_name = 'products'
urlpatterns = [
    path('', index, name='index'),
    path('companies/', companies_list, name='companies_list'),
    path('companies/add', create_company, name='register_avia'),
    path('companies/<slug:company_slug>/', edit_company, name='edit_company'),
]