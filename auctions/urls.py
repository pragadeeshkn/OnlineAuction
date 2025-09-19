from django.urls import path
from . import views, admin_views

urlpatterns = [
    path('', views.home, name='home'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('add-to-watchlist/<int:pk>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove-from-watchlist/<int:pk>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('my-watchlist/', views.my_watchlist, name='my_watchlist'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('my-bids/', views.my_bids, name='my_bids'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='user_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('toggle-watchlist/<int:pk>/', views.toggle_watchlist, name='toggle_watchlist'),
    path('won-auctions/', views.won_auctions, name='won_auctions'),
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
]