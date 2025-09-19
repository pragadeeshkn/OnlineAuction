from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from auctions.models import Category, Listing
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate the database with sample auction data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample categories...')
        categories = [
            'Electronics',
            'Collectibles',
            'Art',
            'Jewelry',
            'Books',
            'Sports',
            'Home & Garden',
            'Fashion',
            'Toys',
            'Automotive'
        ]
        
        category_objects = []
        for cat_name in categories:
            slug = cat_name.lower().replace(' ', '-').replace('&', 'and')
            cat, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={'slug': slug}
            )
            category_objects.append(cat)
            if created:
                self.stdout.write(f'Created category: {cat_name}')
        
        # Create sample users if they don't exist
        self.stdout.write('Creating sample users...')
        users = []
        for i in range(1, 4):
            username = f'user{i}'
            email = f'user{i}@example.com'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            if created:
                user.set_password('password123')
                user.first_name = f'User{i}'
                user.last_name = 'Test'
                user.save()
                self.stdout.write(f'Created user: {username}')
            users.append(user)
        
        # Create sample listings
        self.stdout.write('Creating sample listings...')
        sample_listings = [
            {
                'title': 'Vintage Rolex Watch',
                'description': 'Authentic vintage Rolex Submariner watch from 1980s. In excellent condition with original box and papers.',
                'starting_bid': 5000.00,
                'category': 'Jewelry',
                'seller': users[0]
            },
            {
                'title': 'iPhone 15 Pro Max',
                'description': 'Brand new iPhone 15 Pro Max 256GB in Natural Titanium. Unopened box with full warranty.',
                'starting_bid': 1200.00,
                'category': 'Electronics',
                'seller': users[1]
            },
            {
                'title': 'Original Oil Painting',
                'description': 'Beautiful original oil painting of a landscape. Signed by local artist, framed and ready to hang.',
                'starting_bid': 250.00,
                'category': 'Art',
                'seller': users[2]
            },
            {
                'title': 'Vintage Baseball Cards Collection',
                'description': 'Collection of 50 vintage baseball cards from the 1960s-1980s. Includes rookie cards and rare editions.',
                'starting_bid': 150.00,
                'category': 'Collectibles',
                'seller': users[0]
            },
            {
                'title': 'Designer Handbag',
                'description': 'Authentic designer handbag in excellent condition. Comes with dust bag and authenticity card.',
                'starting_bid': 300.00,
                'category': 'Fashion',
                'seller': users[1]
            }
        ]
        
        for listing_data in sample_listings:
            category = Category.objects.get(name=listing_data['category'])
            listing, created = Listing.objects.get_or_create(
                title=listing_data['title'],
                defaults={
                    'description': listing_data['description'],
                    'starting_bid': listing_data['starting_bid'],
                    'current_bid': listing_data['starting_bid'],
                    'category': category,
                    'seller': listing_data['seller'],
                    'end_date': timezone.now() + timedelta(days=7),
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created listing: {listing.title}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data!'))
        self.stdout.write('You can now access the application at http://127.0.0.1:8000/')
        self.stdout.write('Admin panel: http://127.0.0.1:8000/admin/ (username: admin, password: admin123)')