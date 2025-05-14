from django.shortcuts import render
from .serializers import UserSerializer,NormalUserSerializer,BookingSerializer,TrainSerializer
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking,Train
from .models import generate_pnr
from rest_framework import viewsets
from .permissions import IsNormalUser


User = get_user_model()
class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NormalUsersListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_normal_user=True)
        serializer = NormalUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()  
    serializer_class = TrainSerializer  
    permission_classes=[IsAdminUser]


class BookTicketView(APIView):
    permission_classes = [IsNormalUser, IsAuthenticated]

    def post(self, request):
        train_name=request.data.get("train_name")
        train_number = request.data.get("train_number")
        booking_type = request.data.get("booking_type")
        seat_class = request.data.get("seat_class")
        boarding_station = request.data.get("boarding_station")
        destination_station = request.data.get("destination_station")
        pnr = generate_pnr()
        created_bookings = []
        
        passengers = request.data.get("passengers")

        if passengers:
            # Group booking
            for passenger in passengers:
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
                    "pnr": pnr,
                }

                serializer = BookingSerializer(data=passenger_data)
                if serializer.is_valid():
                    serializer.save()
                    created_bookings.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            # Single booking
            passenger_name = request.data.get("passenger_name")
            passenger_age = request.data.get("passenger_age")
            passenger_gender = request.data.get("passenger_gender")

            if not (passenger_name and passenger_age and passenger_gender):
                return Response({"error": "Passenger details are required for single booking."}, status=status.HTTP_400_BAD_REQUEST)

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
                "pnr": pnr,
            }

            serializer = BookingSerializer(data=passenger_data)
            if serializer.is_valid():
                serializer.save()
                created_bookings.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"pnr": pnr, "bookings": created_bookings}, status=status.HTTP_201_CREATED)



from django.db.models import Q, F, Sum, Count

class ORMAPIView(APIView):
    def get(self, request):
        data = {
            "Filtering": {
                "AC1_Bookings": BookingSerializer(Booking.objects.filter(seat_class='AC1'), many=True).data,
                "High_Fare_Bookings": BookingSerializer(Booking.objects.filter(fare__gt=1000), many=True).data,
            },
            "Related_Lookups": {
                "Bookings_Train_12345": BookingSerializer(Booking.objects.filter(train__train_number='12345'), many=True).data,
                "Trains_With_Confirmed_Bookings": TrainSerializer(Train.objects.filter(bookings__status='Confirmed').distinct(), many=True).data,
            },
            "Aggregation": {
                "Total_Fare": Booking.objects.aggregate(total_fare=Sum('fare')),
                "Booking_Counts_By_Class": list(Booking.objects.values('seat_class').annotate(count=Count('id'))),
            },
            "Annotation": {
                "Train_Booking_Counts": list(Train.objects.annotate(total_bookings=Count('bookings')).values('train_number', 'train_name', 'total_bookings')),
                "Tatkal_Bookings_Per_Train": list(Train.objects.annotate(tatkal_bookings=Count('bookings', filter=Q(bookings__booking_type='Tatkal'))).values('train_number', 'tatkal_bookings')),
            },
            "Q_and_F_Expressions": {
                "AC1_or_Tatkal": BookingSerializer(Booking.objects.filter(Q(seat_class='AC1') | Q(booking_type='Tatkal')), many=True).data,
                "Fare_Greater_Than_Approx": BookingSerializer(Booking.objects.filter(fare__gt=F('fare') - 100), many=True).data,
            }
        }
        return Response(data)
