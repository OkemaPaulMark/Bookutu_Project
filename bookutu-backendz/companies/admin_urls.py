from django.urls import path
from django.views.generic import TemplateView
from accounts.decorators import super_admin_required

# Super Admin Company Management URLs
urlpatterns = [
    path('', super_admin_required(TemplateView.as_view(template_name='admin/companies/list.html')), name='admin_companies_list'),
    path('pending/', super_admin_required(TemplateView.as_view(template_name='admin/companies/pending.html')), name='admin_companies_pending'),
    path('verification/', super_admin_required(TemplateView.as_view(template_name='admin/companies/verification.html')), name='admin_companies_verification'),
    path('<int:company_id>/', super_admin_required(TemplateView.as_view(template_name='admin/companies/detail.html')), name='admin_company_detail_page'),
]
