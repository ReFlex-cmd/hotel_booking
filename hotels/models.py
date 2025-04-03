from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Пользователь с ролями (клиент, владелец отеля, админ)
class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('hotel_owner', 'Hotel Owner'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

    groups = models.ManyToManyField(Group, related_name="hotels_users")
    user_permissions = models.ManyToManyField(Permission, related_name="hotels_users_permissions")

# Отель
class Hotel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.name

# Комната в отеле
class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.TextField()
    is_available = models.BooleanField(default=True)
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.room_type} - {self.hotel.name}"

# Фото отеля или номера
class Photo(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    image = models.BinaryField()  # Фотографии храним в виде BLOB

# Бронирование
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    rooms = models.ManyToManyField(Room)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Cancelled", "Cancelled")
    ])

# Платежи (пока заглушка)
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed")
    ])
