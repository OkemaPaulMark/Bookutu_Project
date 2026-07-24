from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Payment.objects.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = PaymentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return Response({
            'id': payment.id,
            'payment_reference': payment.payment_reference,
            'status': payment.status,
            'amount': payment.amount,
            'currency': payment.currency,
        }, status=status.HTTP_201_CREATED)
