from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Listing, Bid, Category


@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with statistics and overview"""
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=30)
    ).count()
    new_users_today = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=1)
    ).count()
    
    # Listing statistics
    total_listings = Listing.objects.count()
    active_listings = Listing.objects.filter(is_active=True).count()
    ended_listings = Listing.objects.filter(is_ended=True).count()
    new_listings_today = Listing.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=1)
    ).count()
    
    # Bid statistics
    total_bids = Bid.objects.count()
    bids_today = Bid.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=1)
    ).count()
    
    # Category statistics
    category_stats = Category.objects.annotate(
        listing_count=Count('listing', filter=Q(listing__is_active=True))
    ).order_by('-listing_count')[:10]
    
    # Recent activity
    recent_listings = Listing.objects.select_related('seller', 'category').order_by('-created_at')[:5]
    recent_bids = Bid.objects.select_related('listing', 'bidder').order_by('-created_at')[:5]
    
    # Top users by activity
    top_bidders = User.objects.annotate(
        bid_count=Count('bid')
    ).order_by('-bid_count')[:5]
    
    top_sellers = User.objects.annotate(
        listing_count=Count('listing')
    ).order_by('-listing_count')[:5]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'total_listings': total_listings,
        'active_listings': active_listings,
        'ended_listings': ended_listings,
        'new_listings_today': new_listings_today,
        'total_bids': total_bids,
        'bids_today': bids_today,
        'category_stats': category_stats,
        'recent_listings': recent_listings,
        'recent_bids': recent_bids,
        'top_bidders': top_bidders,
        'top_sellers': top_sellers,
    }
    
    return render(request, 'admin/dashboard.html', context)