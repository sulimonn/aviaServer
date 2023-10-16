from users.views import register, login, profile, logout, user_list, create_company
from django.urls import path

app_name = 'users'
urlpatterns = [
    path('register/', register, name='register'),
    path('register-avia/', create_company, name='register_avia'),
    path('login/', login, name='login'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('user_list/', user_list, name='user_list'),

]