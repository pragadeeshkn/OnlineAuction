from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Listing, Bid, Comment, Watchlist, Category, UserProfile
from .forms import SignUpForm, ListingForm, BidForm, CommentForm, UserProfileForm, UserUpdateForm


def home(request):
    listings = Listing.objects.filter(is_active=True).select_related('seller', 'category')
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        listings = listings.filter(category__slug=category_slug)
    
    # Filter by search query
    search_query = request.GET.get('search')
    if search_query:
        listings = listings.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'ending_soon':
        listings = listings.filter(end_date__gt=timezone.now()).order_by('end_date')
    elif status == 'new':
        listings = listings.order_by('-created_at')
    elif status == 'no_bids':
        listings = listings.filter(current_bid__isnull=True)
    
    # Pagination
    paginator = Paginator(listings, 12)  # Show 12 listings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'listings': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_status': status,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
    }
    return render(request, 'auctions/home.html', context)


def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    bids = listing.bids.select_related('bidder')
    comments = listing.comments.select_related('author')
    
    # Check if user has this in watchlist
    is_watched = False
    if request.user.is_authenticated:
        is_watched = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    
    # Handle bidding
    bid_form = None
    if request.user.is_authenticated and listing.is_active and not listing.is_ended():
        if request.method == 'POST' and 'bid_submit' in request.POST:
            bid_form = BidForm(request.POST, listing=listing, user=request.user)
            if bid_form.is_valid():
                bid = bid_form.save(commit=False)
                bid.listing = listing
                bid.bidder = request.user
                bid.save()
                
                # Update listing's current bid
                listing.current_bid = bid.amount
                listing.save()
                
                messages.success(request, 'Your bid has been placed successfully!')
                return redirect('listing_detail', pk=listing.pk)
        else:
            bid_form = BidForm(listing=listing, user=request.user)
    
    # Handle commenting
    comment_form = None
    if request.user.is_authenticated:
        if request.method == 'POST' and 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.listing = listing
                comment.author = request.user
                comment.save()
                messages.success(request, 'Your comment has been posted!')
                return redirect('listing_detail', pk=listing.pk)
        else:
            comment_form = CommentForm()
    
    context = {
        'listing': listing,
        'bids': bids,
        'comments': comments,
        'bid_form': bid_form,
        'comment_form': comment_form,
        'is_watched': is_watched,
        'total_bids': bids.count(),
    }
    return render(request, 'auctions/listing_detail.html', context)


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            messages.success(request, 'Your listing has been created successfully!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm()
    
    return render(request, 'auctions/create_listing.html', {'form': form})


@login_required
def add_to_watchlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    watchlist_item, created = Watchlist.objects.get_or_create(
        user=request.user, 
        listing=listing
    )
    
    if created:
        messages.success(request, 'Added to your watchlist!')
    else:
        messages.info(request, 'This item is already in your watchlist.')
    
    return redirect('listing_detail', pk=listing.pk)


@login_required
def remove_from_watchlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    Watchlist.objects.filter(user=request.user, listing=listing).delete()
    messages.success(request, 'Removed from your watchlist!')
    
    # Redirect to the page the user came from
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('listing_detail', pk=listing.pk)


@login_required
def my_watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user).select_related('listing', 'listing__seller')
    return render(request, 'auctions/watchlist.html', {'watchlist_items': watchlist_items})


@login_required
def my_listings(request):
    listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(listings, 10)  # Show 10 listings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'listings': page_obj,
        'title': 'My Listings',
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
    }
    return render(request, 'auctions/my_listings.html', context)


@login_required
def my_bids(request):
    bids = Bid.objects.filter(bidder=request.user).select_related('listing').order_by('-created_at')
    return render(request, 'auctions/my_bids.html', {'bids': bids})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Welcome to Online Auction! Your account has been created.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    profile = get_object_or_404(UserProfile, user=user)
    user_listings = Listing.objects.filter(seller=user).order_by('-created_at')
    user_bids = Bid.objects.filter(bidder=user).order_by('-created_at')
    won_auctions = Listing.objects.filter(winner=user).order_by('-end_date')
    
    context = {
        'profile_user': user,
        'profile': profile,
        'user_listings': user_listings,
        'user_bids': user_bids,
        'won_auctions': won_auctions,
    }
    return render(request, 'auctions/profile.html', context)


@login_required
def edit_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'auctions/edit_profile.html', context)


@login_required
def won_auctions(request):
    won_listings = Listing.objects.filter(winner=request.user).order_by('-end_date')
    return render(request, 'auctions/won_auctions.html', {'won_auctions': won_listings})


@login_required
def toggle_watchlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    watchlist_item, created = Watchlist.objects.get_or_create(
        user=request.user, 
        listing=listing
    )
    
    if created:
        messages.success(request, 'Added to your watchlist!')
    else:
        watchlist_item.delete()
        messages.success(request, 'Removed from your watchlist.')
    
    return redirect('listing_detail', pk=listing.pk)
