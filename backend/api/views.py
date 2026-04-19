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

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, MobileRegisterSerializer, MobileLoginSerializer
from trips.models import Trip
from trips.serializers import TripSerializer, TripPublicSerializer  
from companies.models import Company, Bus
from bookings.models import Booking

User = get_user_model()

class MobileRegisterView(APIView):
    """
    API endpoint for mobile app user registration
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MobileRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "user_type": user.user_type,
                    "is_verified": user.is_verified
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MobileLoginView(APIView):
    """
    API endpoint for mobile app login
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MobileLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class MobileLogoutView(APIView):
    """
    API endpoint for mobile app logout
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # For mobile logout, we don't need to blacklist tokens
            # The client should discard the tokens on their side
            return Response({
                "success": True,
                "message": "Logged out successfully."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['GET'])
@permission_classes([AllowAny])
def get_trip_seats(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id)
        bus = trip.bus
        
        # Get booked seat numbers for this trip and convert to integers
        booked_seat_strings = list(Booking.objects.filter(
            trip=trip, 
            status__in=['CONFIRMED', 'PENDING']
        ).values_list('seat__seat_number', flat=True))
        
        # Convert string seat numbers to integers for Flutter app
        booked_seats = []
        for seat_str in booked_seat_strings:
            try:
                booked_seats.append(int(seat_str))
            except ValueError:
                # Skip non-integer seat numbers
                pass
        
        return Response({
            'trip_id': trip.id,
            'bus_capacity': bus.total_seats,
            'booked_seats': booked_seats,
            'available_seats': bus.total_seats - len(booked_seats),
            'seat_price': float(trip.base_fare)
        })
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    try:
        trip_id = request.data.get('trip_id')
        seat_numbers = request.data.get('seat_numbers', [])
        passenger_name = request.data.get('passenger_name')
        passenger_phone = request.data.get('passenger_phone')
        
        trip = Trip.objects.get(id=trip_id)
        bus = trip.bus
        
        # Convert seat numbers to strings for consistency
        seat_numbers_str = [str(seat_num) for seat_num in seat_numbers]
        
        # Check if seats are available
        booked_seat_numbers = list(Booking.objects.filter(
            trip=trip,
            status__in=['CONFIRMED', 'PENDING']
        ).values_list('seat__seat_number', flat=True))
        
        for seat_num in seat_numbers_str:
            if seat_num in booked_seat_numbers:
                return Response({'error': f'Seat {seat_num} is already booked'}, status=400)
        
        # Create bookings for each seat (since model expects one booking per seat)
        bookings = []
        total_amount = 0
        
        for seat_num in seat_numbers_str:
            # Find or create bus seat
            try:
                from companies.models import BusSeat
                bus_seat = BusSeat.objects.get(bus=bus, seat_number=seat_num)
            except BusSeat.DoesNotExist:
                # Create seat if it doesn't exist - calculate row number for integer seats
                row_number = ((int(seat_num) - 1) // 4) + 1
                bus_seat = BusSeat.objects.create(
                    bus=bus,
                    seat_number=seat_num,
                    row_number=row_number,
                    seat_position='REGULAR',
                    seat_type='REGULAR'
                )
            
            booking = Booking.objects.create(
                trip=trip,
                passenger=request.user,
                seat=bus_seat,
                passenger_name=passenger_name,
                passenger_phone=passenger_phone,
                base_fare=trip.base_fare,
                total_amount=trip.base_fare,
                status='PENDING'
            )
            bookings.append(booking)
            total_amount += trip.base_fare
        
        # Return first booking reference (they'll all have same passenger)
        return Response({
            'booking_id': bookings[0].id,
            'booking_reference': bookings[0].booking_reference,
            'total_amount': float(total_amount),
            'seat_numbers': seat_numbers,
            'status': bookings[0].status
        })
        
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
