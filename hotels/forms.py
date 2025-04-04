from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Hotel, Room, Booking, Photo, Review


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'phone_number')


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        exclude = ('owner', 'created_at', 'updated_at', 'rating')


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ('hotel', 'created_at', 'updated_at')


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('check_in', 'check_out', 'num_adults', 'num_children', 'special_requests')


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('image', 'caption', 'is_main')