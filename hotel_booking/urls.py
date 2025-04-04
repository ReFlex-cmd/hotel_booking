from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from hotels import views

urlpatterns = [
    # Basic pages
    path('', views.home, name='home'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),

    # User authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),

    # Hotel owner functions
    path('hotels/create/', views.create_hotel, name='create_hotel'),
    path('hotels/manage/', views.manage_hotels, name='manage_hotels'),
    path('hotels/<int:hotel_id>/add_room/', views.add_room, name='add_room'),
    path('hotels/<int:hotel_id>/upload_photo/', views.upload_hotel_photo, name='upload_hotel_photo'),

    # Booking functions
    path('rooms/<int:room_id>/book/', views.book_room, name='book_room'),
    path('bookings/<int:booking_id>/confirmation/', views.booking_confirmation, name='booking_confirmation'),
    path('bookings/<int:booking_id>/review/', views.add_review, name='add_review'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
