from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# Пользователь с ролями (клиент, владелец отеля, админ)
class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('hotel_owner', 'Hotel Owner'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(Group, related_name="hotels_users")
    user_permissions = models.ManyToManyField(Permission, related_name="hotels_users_permissions")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# Отель
class Hotel(models.Model):
    STAR_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=255)
    description = models.TextField()

    # Подробный адрес
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    # Геолокация
    latitude = models.FloatField()
    longitude = models.FloatField()

    # Рейтинг и категория
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    star_category = models.IntegerField(choices=STAR_CHOICES, default=3)

    # Время заезда/выезда
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='12:00')

    # Контактная информация
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_star_category_display()})"


# Комната в отеле
class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.CharField(max_length=100)
    room_number = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(default=2)

    # Количество доступных номеров данного типа
    quantity = models.IntegerField(default=1)

    # Удобства в номере
    amenities = models.TextField()
    has_wifi = models.BooleanField(default=True)
    has_air_conditioning = models.BooleanField(default=True)
    has_tv = models.BooleanField(default=True)
    has_kitchen = models.BooleanField(default=False)
    has_private_bathroom = models.BooleanField(default=True)

    size_sqm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room_type} - {self.hotel.name}"


# Фото отеля или номера
class Photo(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    image = models.ImageField(upload_to='hotel_photos/')
    caption = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(hotel__isnull=False) | models.Q(room__isnull=False),
                name='photo_belongs_to_hotel_or_room'
            )
        ]

    def __str__(self):
        if self.hotel:
            return f"Photo for {self.hotel.name}"
        return f"Photo for {self.room.room_type} at {self.room.hotel.name}"


# Бронирование
class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    rooms = models.ManyToManyField(Room, through='BookingRoom')
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Гости
    num_adults = models.IntegerField(default=1)
    num_children = models.IntegerField(default=0)

    # Дополнительная информация
    special_requests = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username} - {self.status}"

    def save(self, *args, **kwargs):
        # Автоматический расчет количества дней
        if not self.pk:  # Только при создании
            days = (self.check_out - self.check_in).days
            if days <= 0:
                raise ValueError("Check-out date must be after check-in date")
        super().save(*args, **kwargs)


# Промежуточная модель для бронирования комнат с количеством
class BookingRoom(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)  # Сохраняем цену на момент бронирования

    def __str__(self):
        return f"{self.quantity} x {self.room.room_type} for Booking #{self.booking.id}"


# Платежи
class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("paypal", "PayPal"),
        ("bank_transfer", "Bank Transfer"),
        ("cash", "Cash"),
        ("other", "Other"),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status} - {self.amount} руб."

    def save(self, *args, **kwargs):
        if self.status == "completed" and not self.payment_date:
            self.payment_date = timezone.now()
        super().save(*args, **kwargs)


# Отзывы о проживании
class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.booking.user.username} - {self.rating}/5"