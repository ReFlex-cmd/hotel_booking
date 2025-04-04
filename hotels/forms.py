from django import forms
from .models import Photo, Hotel, Room

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('image', 'caption', 'is_main')