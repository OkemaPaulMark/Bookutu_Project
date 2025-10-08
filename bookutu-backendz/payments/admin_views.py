from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
from .models import Payment, CompanyEarnings, Refund
from accounts.permissions import IsSuperAdmin
from companies.models import Company


class PlatformFinancialStatsView(APIView):
    """
    Platform financial statistics for super admin
    """
    permission_classes = [IsSuperAdmin]
    
    def get(self, request):
        today = timezone.now().date()
        
        # Overall financial stats
        financial_stats = {
            'total_revenue': float(
                Payment.objects.filter(status='COMPLETED').aggregate(
                    total=Sum('amount')
                )['total'] or 0
            ),
            'today_revenue': float(
                Payment.objects.filter(
                    status='COMPLETED',
                    completed_at__date=today
                ).aggregate(total=Sum('amount'))['total'] or 0
            ),
            'pending_payments': float(
                Payment.objects.filter(status='PENDING').aggregate(
                    total=Sum('amount')
                )['total'] or 0
            ),
            'total_refunds': float(
                Refund.objects.filter(status='COMPLETED').aggregate(
                    total=Sum('amount')
                )['total'] or 0
            ),
            'platform_commission': float(
                CompanyEarnings.objects.aggregate(
                    total=Sum('platform_commission')
                )['total'] or 0
            ),
            'pending_payouts': float(
                CompanyEarnings.objects.filter(
                    date__lte=today
                ).aggregate(total=Sum('net_earnings'))['total'] or 0
            )
        }
        
        # Payment method breakdown
        payment_methods = Payment.objects.filter(
            status='COMPLETED'
        ).values('payment_method').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-total_amount')
        
        financial_stats['payment_methods'] = [
            {
                'method': method['payment_method'],
                'count': method['count'],
                'total_amount': float(method['total_amount'])
            }
            for method in payment_methods
        ]
        
        # Top earning companies
        top_companies = CompanyEarnings.objects.values(
            'company__name'
        ).annotate(
            total_earnings=Sum('gross_revenue'),
            total_commission=Sum('platform_commission')
        ).order_by('-total_earnings')[:10]
        
        financial_stats['top_earning_companies'] = [
            {
                'company_name': company['company__name'],
                'total_earnings': float(company['total_earnings'] or 0),
                'total_commission': float(company['total_commission'] or 0)
            }
            for company in top_companies
        ]
        
        return Response(financial_stats)


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def company_earnings_report(request):
    """
    Detailed company earnings report
    """
    # Get date range from query params
    days = int(request.query_params.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    earnings = CompanyEarnings.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('company').order_by('-gross_revenue')
    
    earnings_data = []
    for earning in earnings:
        earnings_data.append({
            'company_name': earning.company.name,
            'date': earning.date,
            'total_bookings': earning.total_bookings,
            'gross_revenue': float(earning.gross_revenue),
            'platform_commission': float(earning.platform_commission),
            'net_earnings': float(earning.net_earnings),
            'commission_rate': earning.company.commission_rate
        })
    
    return Response({
        'earnings': earnings_data,
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        },
        'summary': {
            'total_gross_revenue': float(
                earnings.aggregate(total=Sum('gross_revenue'))['total'] or 0
            ),
            'total_commission': float(
                earnings.aggregate(total=Sum('platform_commission'))['total'] or 0
            ),
            'total_net_earnings': float(
                earnings.aggregate(total=Sum('net_earnings'))['total'] or 0
            )
        }
    })


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def process_company_payout(request, company_id):
    """
    Process payout for a specific company
    """
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return Response({'error': 'Company not found'}, status=404)
    
    # Calculate pending earnings
    pending_earnings = CompanyEarnings.objects.filter(
        company=company,
        date__lte=timezone.now().date()
    ).aggregate(total=Sum('net_earnings'))['total'] or 0
    
    if pending_earnings <= 0:
        return Response({'error': 'No pending earnings for this company'}, status=400)
    
    # In a real implementation, this would integrate with payment gateway
    # to process the actual payout
    
    return Response({
        'message': f'Payout of {pending_earnings} processed for {company.name}',
        'amount': float(pending_earnings),
        'company': company.name
    })
