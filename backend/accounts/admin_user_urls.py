from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView

# Super Admin User Management URLs
urlpatterns = [
    path('', staff_member_required(TemplateView.as_view(template_name='admin/users/list.html')), name='admin_users_list'),
    path('passengers/', staff_member_required(TemplateView.as_view(template_name='admin/users/passengers.html')), name='admin_passengers'),
    path('staff/', staff_member_required(TemplateView.as_view(template_name='admin/users/staff.html')), name='admin_staff'),
]
