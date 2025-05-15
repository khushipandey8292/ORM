from rest_framework.test import APITestCase
from rest_framework import status

# class UserRegistrationTest(APITestCase):
#     def test_register_user_successfully(self):
#         data = {
#             "username": "khushi",
#             "email": "khushi@example.com",
#             "password": "password123"
#         }
#         response = self.client.post('/register/', data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         print(response.__dict__)

# from django.contrib.auth import get_user_model
# User = get_user_model()
# class LoginTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username="khushi",
#             email="khushi@example.com",
#             password="password123"
#         )

#     def test_login_success(self):
#         data = {
#             "username": "khushi",
#             "password": "password123"
#         }

#         response = self.client.post('/login/', data, format='json')

#         self.assertEqual(response.status_code, 200)
#         self.assertIn("message", response.data)
#         self.assertEqual(response.data["message"], "Login successful")

#     def test_login_invalid_password(self):
#         data = {
#             "username": "khushi",
#             "password": "wrongpassword"
#         }

#         response = self.client.post('/login/', data, format='json')

#         self.assertEqual(response.status_code, 401)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Invalid credentials")

#     def test_login_missing_fields(self):
#         data = {
#             "username": "khushi"
#             # password is missing
#         }

#         response = self.client.post('/login/', data, format='json')

#         self.assertEqual(response.status_code, 401)
#         self.assertIn("error", response.data)


# from rest_framework.test import APIClient

# from rest_framework.test import APITestCase, APIClient
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class TrainViewSetTest(APITestCase):
#     def setUp(self):
#         self.admin_user = User.objects.create_user(
#             username='adminuser',
#             password='adminpass',
#             is_staff=True,
#             is_superuser=True        
#         )
#         headers={
#             ""
#         }

#     def test_train_create(self):
#         data = {
#             "train_number": "12346",
#             "train_name": "SuperFast Express",
#             "source_station": "Delhi",
#             "destination_station": "Mumbai",
#             "start_time": "10:00:00",
#             "end_time": "20:00:00",
#             "departure_date": "2025-06-01",
#             "arrival_date": "2025-06-02",
#             "intermediate_stops": ["Agra", "Jaipur", "Surat"],
#             "train_type": "Express",
#             "seat_classes": ["Sleeper", "AC1", "AC2"],
#             "total_seats_sleeper": 150,
#             "total_seats_ac1": 50,
#             "total_seats_ac2": 75,
#             "fare_normal": {"Sleeper": 2, "AC1": 5, "AC2": 4},
#             "fare_tatkal": {"Sleeper": 3, "AC1": 7, "AC2": 6},
#             "total_distance": 500,
#             "train_status": True,
#             "duration": "12:00"
#         }
#         header=header

#         response = self.client.post("/api/trains/", data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
