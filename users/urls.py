from users.views import register, login, profile, logout, user_list, companies_list, create_company, point, grant_access, update_perm, delete_user, delete_company
from django.urls import path

app_name = 'users'
urlpatterns = [
    path('register/', register, name='register'),
    path('add-company/', create_company, name='register_avia'),
    path('login/', login, name='login'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('inspectors/', user_list, name='user_list'),
    path('companies/', companies_list, name='companies_list'),
    path('<slug:user_slug>/', point, name='point'),
    path('<slug:user_slug>/delete', delete_user, name='delete_user'),
    path('<slug:company_slug>/delete', delete_company, name='delete_company'),
    path('grant_access/<slug:user_slug>/', grant_access, name='grant_access'),
    path('update-permission/<slug:user_slug>/', update_perm, name='update_perm'),

]