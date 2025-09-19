from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Listing, Bid, Comment, Watchlist, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'listing_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def listing_count(self, obj):
        return obj.listing_set.filter(is_active=True).count()
    listing_count.short_description = 'Active Listings'


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller_link', 'starting_bid', 'current_bid', 'is_active', 'end_date', 'bid_count', 'view_listing']
    list_filter = ['is_active', 'category', 'created_at', 'end_date']
    search_fields = ['title', 'description', 'seller__username']
    date_hierarchy = 'end_date'
    readonly_fields = ['created_at', 'bid_count', 'view_listing']
    list_per_page = 25
    
    def seller_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.seller.id])
        return format_html('<a href="{}">{}</a>', url, obj.seller.username)
    seller_link.short_description = 'Seller'
    
    def bid_count(self, obj):
        return obj.bid_set.count()
    bid_count.short_description = 'Total Bids'
    
    def view_listing(self, obj):
        url = reverse('listing_detail', args=[obj.pk])
        return format_html('<a href="{}" target="_blank">View on Site</a>', url)
    view_listing.short_description = 'View on Site'


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['listing_link', 'bidder_link', 'amount', 'created_at', 'is_winning_bid']
    list_filter = ['created_at', 'listing__is_active']
    search_fields = ['listing__title', 'bidder__username']
    list_per_page = 50
    
    def listing_link(self, obj):
        url = reverse('admin:auctions_listing_change', args=[obj.listing.id])
        return format_html('<a href="{}">{}</a>', url, obj.listing.title[:30] + '...' if len(obj.listing.title) > 30 else obj.listing.title)
    listing_link.short_description = 'Listing'
    
    def bidder_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.bidder.id])
        return format_html('<a href="{}">{}</a>', url, obj.bidder.username)
    bidder_link.short_description = 'Bidder'
    
    def is_winning_bid(self, obj):
        if obj.listing.is_ended and obj.listing.winner == obj.bidder:
            return format_html('<span style="color: green;">✓ Winner</span>')
        elif obj.listing.is_ended:
            return format_html('<span style="color: red;">✗ Lost</span>')
        else:
            return format_html('<span style="color: blue;">Active</span>')
    is_winning_bid.short_description = 'Status'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['listing_link', 'author_link', 'short_content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['listing__title', 'author__username', 'content']
    list_per_page = 50
    
    def listing_link(self, obj):
        url = reverse('admin:auctions_listing_change', args=[obj.listing.id])
        return format_html('<a href="{}">{}</a>', url, obj.listing.title[:30] + '...' if len(obj.listing.title) > 30 else obj.listing.title)
    listing_link.short_description = 'Listing'
    
    def author_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.username)
    author_link.short_description = 'Author'
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'listing_link', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'listing__title']
    list_per_page = 50
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def listing_link(self, obj):
        url = reverse('admin:auctions_listing_change', args=[obj.listing.id])
        return format_html('<a href="{}">{}</a>', url, obj.listing.title[:30] + '...' if len(obj.listing.title) > 30 else obj.listing.title)
    listing_link.short_description = 'Listing'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'location', 'bio_short']
    search_fields = ['user__username', 'location', 'bio']
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def bio_short(self, obj):
        return obj.bio[:50] + '...' if obj.bio and len(obj.bio) > 50 else (obj.bio or '')
    bio_short.short_description = 'Bio'
