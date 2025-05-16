from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Train,Booking
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
      # Create a user and set is_normal_user=True
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
        fields = '__all__'  # Include all train fields
        

    def validate(self, data):
         # Get source and destination in lowercase for comparison
        source = data.get('source_station', '').strip().lower()
        dest = data.get('destination_station', '').strip().lower()
    
        if source == dest:   # Source and destination should not be the same
            raise serializers.ValidationError("Source and destination stations cannot be the same.")

        if data.get('start_time') == data.get('end_time'):   # Start and end time should not be the same
            raise serializers.ValidationError("Start time and end time cannot be the same.")

        if data.get('arrival_date') < data.get('departure_date'): # Arrival date must not be before departure
            raise serializers.ValidationError("Arrival date cannot be before departure date.")

        if data.get('arrival_time') == data.get('departure_time'): # Arrival time and departure time  should not be same
            raise serializers.ValidationError("Arrival time and departure time cannot be the same.")

        if not isinstance(data.get('seat_classes'), list):  # Seat classes should be a list
            raise serializers.ValidationError("Seat classes must be a list.")
        
        if not isinstance(data.get('intermediate_stops'), list):  # intermediate_stops should be a list
            raise serializers.ValidationError("Intermediate stops must be a list.")
        return data



from decimal import Decimal
from .models import Booking, PantryItem, BookingPantry

class PantryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PantryItem
        fields = ['id', 'name', 'price']


class BookingPantrySerializer(serializers.ModelSerializer):
    item = serializers.CharField()  # Accept and return item name
    price = serializers.DecimalField(source='item_obj.price', read_only=True, max_digits=7, decimal_places=2)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = BookingPantry
        fields = ['id', 'booking', 'item', 'price', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()

    def validate(self, data):
        booking = data.get('booking')
        if booking and not booking.wants_pantry:
            raise serializers.ValidationError("Cannot order pantry items. This booking has not opted for pantry.")
        return data

    def create(self, validated_data):
        item_name = validated_data.pop('item')
        try:
            item_obj = PantryItem.objects.get(name__iexact=item_name)
        except PantryItem.DoesNotExist:
            raise serializers.ValidationError({'item': f"Pantry item '{item_name}' not found."})
        validated_data['item'] = item_obj
        return BookingPantry.objects.create(**validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['item'] = instance.item.name  # Show item name in response
        return rep



class BookingSerializer(serializers.ModelSerializer):
    train_name=serializers.SerializerMethodField(read_only=True,)
    train_number = serializers.CharField(write_only=True) 
    fare = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    
    # pnr = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'train_number','train_name', 'passenger_name', 'passenger_age', 'passenger_gender',
            'seat_class', 'booking_type', 'boarding_station', 'destination_station',
            'fare', 'pnr', 'status', 'seat_number','meal'
        ]
        read_only_fields = ['fare',  'status', 'seat_number']
      
    def get_train_name(self, obj):
        return obj.train.train_name if obj.train else None   # Return train name if train exists
      
    def validate_passenger_age(self, value):
        
        if value <= 0: # Age should be more than 0
            raise serializers.ValidationError("Passenger age must be greater than 0.")
        if value > 120:    # Age should not be more than 120
            raise serializers.ValidationError("Passenger age seems unrealistic.")
        return value
    
    def validate(self, attrs):
        train_number = attrs.get('train_number')
        seat_class = attrs.get('seat_class')
        booking_type = attrs.get('booking_type')
        boarding_station = attrs.get('boarding_station')
        destination_station = attrs.get('destination_station') 
        
        
          # Get the train using train number
        try:
            train = Train.objects.get(train_number=train_number)
        except Train.DoesNotExist:
            raise serializers.ValidationError(f"Train with number {train_number} not found.")
        
         # Get passengers list if it's a group booking
        passengers = self.initial_data.get("passengers", [])
        if len(passengers) > 6:
            raise serializers.ValidationError("You cannot add more than 6 passengers.")
        
          # Calculate fare using train method
        try:
            fare = train.get_fare(seat_class, booking_type, boarding_station, destination_station)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        
          # Save the train and fare in validated data
        attrs['train'] = train
        attrs['fare'] = Decimal(str(fare)).quantize(Decimal('0.01'))
        return attrs

    def create(self, validated_data):
        validated_data.pop('train_number', None)
        train = validated_data['train']
        seat_class = validated_data['seat_class'].lower()
        existing_seat_count = Booking.objects.filter(train=train, seat_class=seat_class).count() + 1   # Count how many seats are already booked for this class
        
        
        # Assign seat number and reduce seat count
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

        train.save() # Save updated seat availability
        validated_data['seat_number'] = seat_number # Add seat number to data
        pnr = self.initial_data.get("pnr")
        if pnr:
            validated_data["pnr"] = pnr
        return Booking.objects.create(**validated_data)   # Create and return booking

