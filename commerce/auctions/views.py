from argparse import Action
from nturl2path import url2pathname
from turtle import title
from django.contrib.auth import authenticate, login, logout, get_user
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from .models import User, Auction, Bid, Watchlist, Comment, Category

class CreateListingForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Listing Title (200 Characters Max)'}))
    description = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'name':'body', 'style': 'height: 3em;', 'placeholder': 'Description'}))
    starting_bid = forms.DecimalField(max_digits=9, decimal_places=2)
    url = forms.URLField(widget=forms.TextInput(attrs={'placeholder': 'Input image URL here'}))
    category = forms.ChoiceField(choices=Category.category_choices)

class AddToWatchlistForm(forms.Form):
    pass

class RemoveFromWatchlistForm(forms.Form):
    pass

class BidForm(forms.Form):
    def __init__(self,*args,**kwargs):
        value = kwargs['bid']
        super(BidForm,self).__init__(*args,**kwargs)
        self.fields['bid'] = forms.DecimalField(max_digits=9, decimal_places=2, widget=forms.TextInput(attrs={'placeholder':'test'}))

    # bid = forms.DecimalField(max_digits=9, decimal_places=2)

def index(request):
    auctions = Auction.objects.all()
    return render(request, "auctions/index.html" , {
        "Auctions": auctions
    })

@login_required
def create(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            url = form.cleaned_data["url"]
            category = form.cleaned_data ["category"]
            starting_bid = form.cleaned_data["starting_bid"]
            # Create db entry from data
            auction = Auction(
                title=title, 
                description=description, 
                imageURL=url, 
                category=category, 
                starting_bid=starting_bid, 
                username=User.objects.get(username=get_user(request).get_username()) 
            )
            auction.save()

            return render(request, "auctions/create.html", {
                "CreateListingForm": CreateListingForm(),
                "message" : "Listing Created"
            })

    return render(request, "auctions/create.html", {
        "CreateListingForm": CreateListingForm()
    })

def listing(request, id):
    # Clicking on a listing should take users to a page specific to that listing. 
    listing = Auction.objects.get(id=int(id))
    user = User.objects.get(username=get_user(request).get_username())
    # If the user is signed in, the user should be able to add the item to their “Watchlist.” 
    # If the item is already on the watchlist, the user should be able to remove it.
    if request.method == "POST": 
        if 'watchlist_add_btn' in request.POST:
            add_to_watchlist_form = AddToWatchlistForm(request.POST)
            if add_to_watchlist_form.is_valid():
                watchlist_entry = Watchlist(
                    auctionID=listing,
                    username=User.objects.get(username=get_user(request).get_username()) 
                )
                watchlist_entry.save()

        if 'watchlist_remove_btn' in request.POST:
            remove_from_watchlist_form = RemoveFromWatchlistForm(request.POST)
            if remove_from_watchlist_form.is_valid():
                print(Watchlist.objects.all())
                Watchlist.objects.filter(username=user, auctionID=listing).delete()
                print(Watchlist.objects.all())

    watchlist = False
    if user != None:
        watchlist = Watchlist.objects.filter(username=user, auctionID=listing).exists()
        
    # TODO
    # If the user is signed in, the user should be able to bid on the item. The bid must be at least as large as the starting bid, 
    # and must be greater than any other bids that have been placed (if any). If the bid doesn’t meet those criteria, the user should be presented with an error.
    bid_message = None
    current_price = listing.starting_bid
    if Bid.objects.filter(auctionID=listing).exists():
        bids = Bid.objects.filter(auctionID=listing)
        current_price = round(bids.aggregate(Max('amount'))['amount__max'],2)

    # 3. If the user is signed in and is the one who created the listing, the user should have the ability to “close” the auction from this page, 
    #    which makes the highest bidder the winner of the auction and makes the listing no longer active.
    # 4. If a user is signed in on a closed listing page, and the user has won that auction, the page should say so.
    # 5. Users who are signed in should be able to add comments to the listing page. The listing page should display all comments that have been made on the listing.
    return render(request, "auctions/listing.html" , {
        "watchlist_form_add": AddToWatchlistForm(),
        "watchlist_form_remove": RemoveFromWatchlistForm(),
        "bid_form":BidForm(bid=current_price),
        "listing":listing,
        "user":user,
        "watchlist":watchlist,
        "current_price":current_price,
        "bid_message":bid_message
    })


@login_required
def watchlist(request):
    # TODO Users who are signed in should be able to visit a Watchlist page, which should display all of the listings that a user has added to their watchlist. 
    # Clicking on any of those listings should take the user to that listing’s page.
    return render(request, "auctions/watchlist.html")


def catagories(request):
    # TODO Users should be able to visit a page that displays a list of all listing categories. 
    # Clicking on the name of any category should take the user to a page that displays all of the active listings in that category.
    return render(request, "auctions/categories.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
