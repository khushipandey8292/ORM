from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Train,Booking
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_normal_user=True
        )
        return user

class NormalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = '__all__'
        

    def validate(self, data):
        source = data.get('source_station', '').strip().lower()
        dest = data.get('destination_station', '').strip().lower()

        if source == dest:
            raise serializers.ValidationError("Source and destination stations cannot be the same.")

        if data.get('start_time') == data.get('end_time'):
            raise serializers.ValidationError("Start time and end time cannot be the same.")

        if data.get('arrival_date') < data.get('departure_date'):
            raise serializers.ValidationError("Arrival date cannot be before departure date.")

        if data.get('arrival_date') == data.get('departure_date'):
            raise serializers.ValidationError("Arrival date and departure date cannot be the same.")

        if not isinstance(data.get('seat_classes'), list):
            raise serializers.ValidationError("Seat classes must be a list.")
        
        if not isinstance(data.get('intermediate_stops'), list):
            raise serializers.ValidationError("Intermediate stops must be a list.")
        return data


from rest_framework import serializers
from .models import Booking, Train
from decimal import Decimal


class BookingSerializer(serializers.ModelSerializer):
    train_name=serializers.SerializerMethodField(read_only=True,)
    train_number = serializers.CharField(write_only=True) 
    fare = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    pnr = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'train_number','train_name', 'passenger_name', 'passenger_age', 'passenger_gender',
            'seat_class', 'booking_type', 'boarding_station', 'destination_station',
            'fare', 'pnr', 'status', 'seat_number'
        ]
        read_only_fields = ['fare', 'pnr', 'status', 'seat_number']
      
    def get_train_name(self, obj):
        return obj.train.train_name if obj.train else None  
      
    def validate_passenger_age(self, value):
        if value <= 0:
            raise serializers.ValidationError("Passenger age must be greater than 0.")
        if value > 120:
            raise serializers.ValidationError("Passenger age seems unrealistic.")
        return value
    
    def validate(self, attrs):
        train_number = attrs.get('train_number')
        seat_class = attrs.get('seat_class')
        booking_type = attrs.get('booking_type')
        boarding_station = attrs.get('boarding_station')
        destination_station = attrs.get('destination_station') 
        
        try:
            train = Train.objects.get(train_number=train_number)
        except Train.DoesNotExist:
            raise serializers.ValidationError(f"Train with number {train_number} not found.")
        
        passengers = self.initial_data.get("passengers", [])
        if len(passengers) > 6:
            raise serializers.ValidationError("You cannot add more than 6 passengers.")
        
        try:
            fare = train.get_fare(seat_class, booking_type, boarding_station, destination_station)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        
        attrs['train'] = train
        attrs['fare'] = Decimal(str(fare)).quantize(Decimal('0.01'))
        return attrs

    def create(self, validated_data):
        validated_data.pop('train_number', None)
        train = validated_data['train']
        seat_class = validated_data['seat_class'].lower()
        existing_seat_count = Booking.objects.filter(train=train, seat_class=seat_class).count() + 1
        
        if seat_class == "sleeper":
            if train.available_seats_sleeper <= 0:
                raise serializers.ValidationError("No available Sleeper seats.")
            train.available_seats_sleeper -= 1
            seat_number = f"S{existing_seat_count}"
        elif seat_class == "ac1":
            if train.available_seats_ac1 <= 0:
                raise serializers.ValidationError("No available AC1 seats.")
            train.available_seats_ac1 -= 1
            seat_number = f"A1-{existing_seat_count}"
        elif seat_class == "ac2":
            if train.available_seats_ac2 <= 0:
                raise serializers.ValidationError("No available AC2 seats.")
            train.available_seats_ac2 -= 1
            seat_number = f"A2-{existing_seat_count}"
        else:
            raise serializers.ValidationError("Invalid seat class.")

        train.save()
        validated_data['seat_number'] = seat_number
        return Booking.objects.create(**validated_data)

