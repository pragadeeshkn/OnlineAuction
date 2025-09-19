from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from auctions.models import Listing, Bid
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Automatically close ended auctions and determine winners'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually closing auctions',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all active listings that have ended
        ended_listings = Listing.objects.filter(
            is_active=True,
            end_date__lte=timezone.now()
        )
        
        closed_count = 0
        
        for listing in ended_listings:
            if not dry_run:
                # Get the highest bid
                highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
                
                if highest_bid:
                    # Set the winner
                    listing.winner = highest_bid.bidder
                    listing.current_bid = highest_bid.amount
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Auction "{listing.title}" won by {highest_bid.bidder.username} for ${highest_bid.amount}'
                        )
                    )
                    
                    # Send notification email to winner
                    try:
                        send_mail(
                            subject=f'Congratulations! You won the auction for {listing.title}',
                            message=f'You have successfully won the auction for "{listing.title}" with a bid of ${highest_bid.amount}. Please contact the seller {listing.seller.username} to arrange payment and delivery.',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[highest_bid.bidder.email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to send email to winner: {e}')
                        )
                    
                    # Send notification email to seller
                    try:
                        send_mail(
                            subject=f'Your auction for {listing.title} has ended',
                            message=f'Your auction for "{listing.title}" has ended. The winner is {highest_bid.bidder.username} with a bid of ${highest_bid.amount}. Please contact them to arrange payment and delivery.',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[listing.seller.email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to send email to seller: {e}')
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Auction "{listing.title}" ended with no bids')
                    )
                    
                    # Send notification to seller about no bids
                    try:
                        send_mail(
                            subject=f'Your auction for {listing.title} has ended',
                            message=f'Your auction for "{listing.title}" has ended with no bids. You can relist the item if you wish.',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[listing.seller.email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to send email to seller: {e}')
                        )
                
                # Mark listing as inactive
                listing.is_active = False
                listing.save()
            else:
                self.stdout.write(
                    self.style.WARNING(f'Dry run: Would close auction "{listing.title}"')
                )
            
            closed_count += 1
        
        if closed_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No auctions to close.')
            )
        else:
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'Dry run complete. {closed_count} auctions would be closed.')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully closed {closed_count} auctions.')
                )