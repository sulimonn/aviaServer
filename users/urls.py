from users.views import register, login, profile, forgot_password, logout, user_list, grant_access, update_perm, delete_user, delete_company, edit_user, point
from django.urls import path

app_name = 'users'
urlpatterns = [
    path('', user_list, name='user_list'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('restore-password/', forgot_password, name='password'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('api/<slug:user_slug>/update-permission', update_perm, name='update_perm'),
    path('<slug:user_slug>/', edit_user, name='edit_user'),
    path('<slug:user_slug>/update-permission/', point, name='permission'),
    path('<slug:user_slug>/delete', delete_user, name='delete_user'),
    path('<slug:company_slug>/delete', delete_company, name='delete_company'),
    path('<slug:user_slug>/grant_access/', grant_access, name='grant_access'),

]