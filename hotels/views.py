from django.shortcuts import render, redirect, get_object_or_404
from .forms import PhotoForm
from .models import User, Hotel, Room, Booking, BookingRoom, Review
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, HotelForm, RoomForm, BookingForm, ReviewForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'hotels/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
    return render(request, 'hotels/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def user_profile(request):
    # Display user info and bookings
    user_bookings = request.user.bookings.all().order_by('-created_at')
    return render(request, 'hotels/profile.html', {'bookings': user_bookings})


def home(request):
    """Homepage view showing featured hotels"""
    featured_hotels = Hotel.objects.filter(is_active=True).order_by('-rating')[:5]
    return render(request, 'hotels/home.html', {'featured_hotels': featured_hotels})


def hotel_list(request):
    """List all available hotels with search functionality"""
    hotels = Hotel.objects.filter(is_active=True)

    # Simple search by location
    search_query = request.GET.get('search', '')
    if search_query:
        hotels = hotels.filter(city__icontains=search_query) | hotels.filter(country__icontains=search_query)

    return render(request, 'hotels/hotel_list.html', {'hotels': hotels, 'search_query': search_query})


def hotel_detail(request, hotel_id):
    """Detailed view of a specific hotel and its rooms"""
    hotel = get_object_or_404(Hotel, id=hotel_id, is_active=True)
    rooms = hotel.rooms.filter(is_available=True)

    # Get available rooms based on date if provided
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    return render(request, 'hotels/hotel_detail.html', {
        'hotel': hotel,
        'rooms': rooms,
        'check_in': check_in,
        'check_out': check_out
    })


@login_required
def create_hotel(request):
    if request.user.role != 'hotel_owner':
        return redirect('home')

    if request.method == 'POST':
        form = HotelForm(request.POST)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.owner = request.user
            hotel.save()
            return redirect('hotel_detail', hotel_id=hotel.id)
    else:
        form = HotelForm()

    return render(request, 'hotels/create_hotel.html', {'form': form})


@login_required
def manage_hotels(request):
    if request.user.role != 'hotel_owner':
        return redirect('home')

    hotels = Hotel.objects.filter(owner=request.user)
    return render(request, 'hotels/manage_hotels.html', {'hotels': hotels})


@login_required
def add_room(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.hotel = hotel
            room.save()
            return redirect('hotel_detail', hotel_id=hotel.id)
    else:
        form = RoomForm()

    return render(request, 'hotels/add_room.html', {'form': form, 'hotel': hotel})


@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_available=True)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user

            # Calculate total price
            check_in = booking.check_in
            check_out = booking.check_out
            days = (check_out - check_in).days
            booking.total_price = room.price_per_night * days

            booking.save()

            # Create the booking-room relationship
            BookingRoom.objects.create(
                booking=booking,
                room=room,
                quantity=1,
                price_per_night=room.price_per_night
            )

            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'hotels/book_room.html', {
        'form': form,
        'room': room,
        'hotel': room.hotel
    })


@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'hotels/booking_confirmation.html', {'booking': booking})


@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='completed')

    # Check if review already exists
    try:
        review = booking.review
        return redirect('booking_detail', booking_id=booking.id)
    except Review.DoesNotExist:
        pass

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()

            # Update hotel rating
            hotel = booking.rooms.first().hotel
            hotel_reviews = Review.objects.filter(booking__rooms__hotel=hotel)
            # avg_rating = hotel_reviews.aggregate(models.Avg('rating'))['rating__avg']
            # hotel.rating = avg_rating
            hotel.save()

            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = ReviewForm()

    return render(request, 'hotels/add_review.html', {'form': form, 'booking': booking})


def upload_hotel_photo(request, hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.hotel = hotel
            photo.save()
            return redirect('hotel_detail', hotel_id=hotel_id)
    else:
        form = PhotoForm()

    return render(request, 'upload_photo.html', {'form': form, 'hotel': hotel})
