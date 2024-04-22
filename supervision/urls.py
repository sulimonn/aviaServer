from django.urls import path
from supervision.views import control, supervise, delete_check_month, add_check_month, dashboard, create_period, move_check
from documents.views import  update_move_check, get_moved, post

app_name = "supervision"

urlpatterns = [
    path('<slug:company_slug>/', control, name='control'),
    path('<slug:company_slug>/edit', control, {'edit': True}, name='edit'),
    path('<slug:company_slug>/dashboard/', dashboard, name='dashboard'),
    path('<slug:company_slug>/check-area-table/', supervise, name='check_area_table'),
    path('<slug:company_slug>/moved/', get_moved, name='moved'),
    path('<slug:company_slug>/add-period/', create_period, name='period'),
    path('api/post', post, name='post'),
    path('api/<int:month_id>/delete/', delete_check_month, name='delete_check_month'),
    path('api/<int:area_id>/<int:month_id>/add/', add_check_month, name='add_check_month'),
    path('api/move-check/<int:area_id>/', move_check, name='move'),
    path('api/post-move-check/<slug:company_slug>/', update_move_check, name='update_move'),

]
