from django.urls import path
from .admin_views import (
    PlatformFinancialStatsView, company_earnings_report, process_company_payout
)

urlpatterns = [
    # Financial Management
    path('admin/financial-stats/', PlatformFinancialStatsView.as_view(), name='admin_financial_stats'),
    path('admin/earnings-report/', company_earnings_report, name='admin_earnings_report'),
    path('admin/companies/<int:company_id>/payout/', process_company_payout, name='admin_process_payout'),
]
