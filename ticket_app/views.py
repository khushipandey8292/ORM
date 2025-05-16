from django.shortcuts import render
from .serializers import UserSerializer,NormalUserSerializer,BookingSerializer,TrainSerializer, PantryItemSerializer, BookingPantrySerializer
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking,Train,PantryItem, BookingPantry
from .models import generate_pnr
from rest_framework import viewsets
# from .permissions import IsNormalUser
from ticket_app.decorators import normal_user_required,admin_required

User = get_user_model()
class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NormalUsersListView(APIView):
    # permission_classes = [IsAdminUser]
    #  use a decorator(like @admin_required) to ensure the user is authenticated and  is an admin if condition is true then perform get operation to view all normal users.
    @admin_required
    def get(self, request):
        users = User.objects.filter(is_normal_user=True)
        serializer = NormalUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# admin can perform crud operation on train model--------------------------------------
class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()  
    serializer_class = TrainSerializer  
    # permission_classes=[IsAuthenticated] 
    #  use a decorator(like @admin_required) to ensure the user is authenticated and  is an admin if condition is true then perform create operation. 
    @admin_required
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    # use a decorator(like @admin_required) to ensure the user is authenticated and  is an admin if condition is true then perform update operation.
    @admin_required
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
        #  use a decorator(like @admin_required) to ensure the user is authenticated and  is an admin if condition is true then perform partial update operation.
    @admin_required
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
        #  use a decorator(like @admin_required) to ensure the user is authenticated and  is an admin if condition is true then perform delete operation.
    @admin_required
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    # permission_classes=[IsAdminUser]


class BookTicketView(APIView):
    # permission_classes = [IsAuthenticated]
    # permission_classes = [IsNormalUser, IsAuthenticated]
    
    
    @normal_user_required
    def post(self, request):
        train_name=request.data.get("train_name")
        train_number = request.data.get("train_number")
        booking_type = request.data.get("booking_type")
        seat_class = request.data.get("seat_class")
        boarding_station = request.data.get("boarding_station")
        destination_station = request.data.get("destination_station")
        meal = request.data.get('meal', False)
        created_bookings = []
        passengers = request.data.get("passengers")# Check if passengers list is provided (group booking case)
        print(passengers)
        if passengers:
            group_pnr = generate_pnr()
            # Group booking
            for passenger in passengers:  # Loop through each passenger and create booking
                passenger_data = {
                    "train_number": train_number,
                    "train_name":train_name,
                    "booking_type": booking_type,
                    "seat_class": seat_class,
                    "boarding_station": boarding_station,
                    "destination_station": destination_station,
                    "passenger_name": passenger.get("name"),
                    "passenger_age": passenger.get("age"),
                    "passenger_gender": passenger.get("gender"),  
                    "pnr": group_pnr ,
                    "meal":meal     
                }

                serializer = BookingSerializer(data=passenger_data)
                if serializer.is_valid():
                    serializer.save()
                    created_bookings.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"pnr": group_pnr, "bookings": created_bookings}, status=status.HTTP_201_CREATED)
        else:
            # Single booking
            passenger_name = request.data.get("passenger_name")
            passenger_age = request.data.get("passenger_age")
            passenger_gender = request.data.get("passenger_gender")
            
               # Check if passenger details are present
            if not (passenger_name and passenger_age and passenger_gender):
                return Response({"error": "Passenger details are required for single booking."}, status=status.HTTP_400_BAD_REQUEST)
            unique_pnr = generate_pnr()
            passenger_data = {
                "train_number": train_number,
                "train_name":train_name,
                "booking_type": booking_type,
                "seat_class": seat_class,
                "boarding_station": boarding_station,
                "destination_station": destination_station,
                "passenger_name": passenger_name,
                "passenger_age": passenger_age,
                "passenger_gender": passenger_gender,
                "pnr": unique_pnr,
                "meal":meal
                  
            }
            
            serializer = BookingSerializer(data=passenger_data)
            if serializer.is_valid():
                serializer.save()
                created_bookings.append(serializer.data)
                return Response({ "bookings": created_bookings}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from django.db.models import Q, F, Sum, Count

class ORMAPIView(APIView):
    def get(self, request):
        data = {
            "Filtering": {
                "AC1_Bookings": BookingSerializer(Booking.objects.filter(seat_class='AC1'), many=True).data,  # Get all bookings where seat class is AC1
                "High_Fare_Bookings": BookingSerializer(Booking.objects.filter(fare__gt=1000), many=True).data,# Get bookings with fare greater than 1000
            },
            "Related_Lookups": {
                "Bookings_Train_12345": BookingSerializer(Booking.objects.filter(train__train_number='12345'), many=True).data, # Get bookings for a specific train number
                "Trains_With_Confirmed_Bookings": TrainSerializer(Train.objects.filter(bookings__status='Confirmed').distinct(), many=True).data, # Get all unique trains that have at least one confirmed booking
            },
            "Aggregation": {
                "Total_Fare": Booking.objects.aggregate(total_fare=Sum('fare')), # Calculate total fare collected from all bookings
                "Booking_Counts_By_Class": list(Booking.objects.values('seat_class').annotate(count=Count('id'))),# Count number of bookings in each seat class
            },
            "Annotation": {
                "Train_Booking_Counts": list(Train.objects.annotate(total_bookings=Count('bookings')).values('train_number', 'train_name', 'total_bookings')),   # Count total bookings for each train
                "Tatkal_Bookings_Per_Train": list(Train.objects.annotate(tatkal_bookings=Count('bookings', filter=Q(bookings__booking_type='Tatkal'))).values('train_number', 'tatkal_bookings')),# Count tatkal bookings per train
            },
            "Q_and_F_Expressions": {
                "AC1_or_Tatkal": BookingSerializer(Booking.objects.filter(Q(seat_class='AC1') | Q(booking_type='Tatkal')), many=True).data, # Get bookings where seat class is AC1 OR booking type is Tatkal
                "Fare_Greater_Than_Approx": BookingSerializer(Booking.objects.filter(fare__gt=F('fare') - 100), many=True).data, # Get bookings where fare is greater than fare - 100 
            }
        }
        return Response(data)
    
    
class PantryItemViewSet(viewsets.ModelViewSet):
    queryset = PantryItem.objects.all()
    serializer_class = PantryItemSerializer
    permission_classes=[IsAdminUser]

class BookingPantryViewSet(viewsets.ModelViewSet):
    queryset = BookingPantry.objects.all()
    serializer_class = BookingPantrySerializer
    
    