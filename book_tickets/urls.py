"""
URL configuration for book_tickets project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from ticket_app.views import RegisterUserView,NormalUsersListView,TrainViewSet,BookTicketView,ORMAPIView,PantryItemViewSet, BookingPantryViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'trains', TrainViewSet) 
router.register(r'pantry-items', PantryItemViewSet)
router.register(r'booking-pantry', BookingPantryViewSet) 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterUserView.as_view(), name='register-user'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('normal-users/', NormalUsersListView.as_view(), name='normal-users-list'),
    path('api/', include(router.urls)), 
    path('book-ticket/', BookTicketView.as_view(), name='book-ticket'),
    path('orm-examples/', ORMAPIView.as_view()),
]
