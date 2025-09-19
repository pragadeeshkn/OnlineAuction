from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Listing, Bid, Comment, UserProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ListingForm(forms.ModelForm):
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="Format: YYYY-MM-DD HH:MM"
    )

    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'end_date', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'starting_bid': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
        }

    def clean_starting_bid(self):
        starting_bid = self.cleaned_data.get('starting_bid')
        if starting_bid and starting_bid <= 0:
            raise forms.ValidationError("Starting bid must be greater than 0.")
        return starting_bid

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        if end_date and end_date <= timezone.now():
            raise forms.ValidationError("End date must be in the future.")
        return end_date


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01', 'placeholder': 'Enter your bid'})
        }

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop('listing', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount:
            raise forms.ValidationError("Please enter a bid amount.")
        
        if self.listing:
            if amount < self.listing.starting_bid:
                raise forms.ValidationError(f"Bid must be at least ${self.listing.starting_bid}.")
            
            highest_bid = self.listing.get_highest_bid()
            if highest_bid and amount <= highest_bid.amount:
                raise forms.ValidationError(f"Bid must be higher than the current highest bid of ${highest_bid.amount}.")
        
        return amount


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your comment here...'})
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'birth_date', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']