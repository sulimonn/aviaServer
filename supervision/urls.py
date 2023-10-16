from django.urls import path
from supervision.views import control, supervise, post, update_check_month, dashboard, move_check, update_move_check, get_moved

app_name = "supervision"

urlpatterns = [
    path('<slug:company_slug>/', control, name='control'),
    path('<slug:company_slug>/dashboard/', dashboard, name='dashboard'),
    path('<slug:company_slug>/check-area-table/', supervise, name='check_area_table'),
    path('<slug:company_slug>/moved/', get_moved, name='moved'),
    path('api/post', post, name='post'),
    path('api/update_check_month/<int:check_month_id>/', update_check_month, name='update_check_month'),
    path('api/move-check/<slug:company_slug>/<int:area_id>/', move_check, name='move'),
    path('api/post-move-check/<slug:company_slug>/', update_move_check, name='update_move'),

]
