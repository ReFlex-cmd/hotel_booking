from django.shortcuts import render, redirect
from .forms import PhotoForm
from .models import Hotel, Room, Photo


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