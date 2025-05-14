from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone
class CustomUser(AbstractUser):
    is_normal_user = models.BooleanField(default=True)  

    def __str__(self):
        return self.username

import random
import string

def generate_pnr():
    return ''.join(random.choices(string.digits, k=8))

def get_current_date():
    return timezone.now().date()

class Train(models.Model):
    train_number = models.CharField(max_length=10, unique=True)
    train_name = models.CharField(max_length=100)
    source_station = models.CharField(max_length=100)
    destination_station = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    departure_date = models.DateField()  
    arrival_date = models.DateField()  
    intermediate_stops = models.JSONField(default=list) 
    train_type = models.CharField(max_length=50)
    seat_classes = models.JSONField()
    total_seats_sleeper = models.IntegerField(default=0)
    total_seats_ac1 = models.IntegerField(default=0)
    total_seats_ac2 = models.IntegerField(default=0)
    available_seats_sleeper = models.IntegerField(default=0)
    available_seats_ac1 = models.IntegerField(default=0)
    available_seats_ac2 = models.IntegerField(default=0)
    fare_normal = models.JSONField(default=dict)  
    fare_tatkal = models.JSONField(default=dict)  
    total_distance = models.IntegerField()
    train_status = models.BooleanField(default=True)  
    duration = models.DurationField()
    
    
    def __str__(self):
        return f"{self.train_name} ({self.train_number})"
  

    def get_station_order(self):
            return [self.source_station] + self.intermediate_stops + [self.destination_station]


    def calculate_distance(self, boarding_station, destination_station):
        station_order = self.get_station_order()

        print(f"Station order: {station_order}")
        print(f"Boarding station: {boarding_station}, Destination station: {destination_station}")

        if boarding_station not in station_order or destination_station not in station_order:
            raise ValueError(f"Invalid boarding or destination station. Boarding: {boarding_station}, Destination: {destination_station}")

        start_index = station_order.index(boarding_station)
        end_index = station_order.index(destination_station)

        if start_index >= end_index:
            raise ValueError("Destination must come after boarding station")

        # Equal segment assumption
        total_segments = len(station_order) - 1
        covered_segments = end_index - start_index

        segment_distance = self.total_distance / total_segments
        return round(segment_distance * covered_segments, 2)

    def get_fare(self, seat_class, booking_type="Normal", boarding_station=None, destination_station=None):
        if not boarding_station or not destination_station:
            return None

        fare_distance = self.calculate_distance(boarding_station, destination_station)
        base_fare = self.get_base_fare(seat_class, booking_type)
        if base_fare is None:
            return None
        return round(base_fare * fare_distance, 2)

    def get_base_fare(self, seat_class, booking_type="Normal"):
        if booking_type == "Tatkal":
            return self.fare_tatkal.get(seat_class)
        return self.fare_normal.get(seat_class)
    
    def save(self, *args, **kwargs):
        if self._state.adding: 
            self.available_seats_sleeper = self.total_seats_sleeper
            self.available_seats_ac1 = self.total_seats_ac1
            self.available_seats_ac2 = self.total_seats_ac2
        super().save(*args, **kwargs)
    
class Booking(models.Model):
    BOOKING_TYPE_CHOICES = [
        ("Normal", "Normal"),
        ("Tatkal", "Tatkal")
    ]

    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="bookings")
    pnr = models.CharField(max_length=8, default=generate_pnr, editable=False)
    passenger_name = models.CharField(max_length=100)
    passenger_age = models.PositiveIntegerField()
    passenger_gender = models.CharField(max_length=10)
    seat_class = models.CharField(max_length=20)  
    booking_type = models.CharField(max_length=10, choices=BOOKING_TYPE_CHOICES)
    boarding_station = models.CharField(max_length=100)
    destination_station = models.CharField(max_length=100)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="Confirmed")
    booking_time = models.DateTimeField(auto_now_add=True)
    seat_number = models.CharField(max_length=10, null=True, blank=True) 
    
    
    def __str__(self):
        return f"{self.passenger_name} - PNR {self.pnr}"
    