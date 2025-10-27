from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from trips.models import Trip
from trips.serializers import TripSerializer, TripPublicSerializer  
from companies.models import Company, Bus

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "user": {"id": user.id, "username": user.username, "email": user.email}
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"success": True, "message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def public_trips(request):
    now = timezone.now().date()
    trips = Trip.objects.filter(
        status="SCHEDULED",
        departure_date__gte=now
    ).select_related("route", "bus", "company").order_by("departure_date", "departure_time")

    serializer = TripPublicSerializer(trips, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def add_trip(request):
    data = request.data.copy()

    # Assign company based on bus
    bus = Bus.objects.get(pk=data['bus'])
    company = bus.company
    data['company'] = company.id

    serializer = TripSerializer(data=data)
    if serializer.is_valid():
        serializer.save(company=company)
        return Response({"message": "Trip added successfully", "trip": serializer.data})
    return Response(serializer.errors, status=400)
