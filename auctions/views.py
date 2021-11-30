from typing_extensions import Required
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Auction_listing, Bid, Comment


def index(request):
    return render(request, "auctions/index.html")


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

@login_required(login_url="/login", redirect_field_name="")
def new_listing(request):

    # if a post is made, add a new listing to the database
    if request.method == "POST":
        # get all the attributes from the request
        user = User.objects.get(pk=request.user.id)
        title = request.POST["title"]
        description = request.POST["description"]
        start_bid = request.POST["start_bid"]
        image_url = request.POST["image"]
        category = request.POST["category"]

        # save in the database
        new_listing = Auction_listing(
            title = title,
            description = description,
            start_bid = start_bid,
            listed_by = user,
            category = category,
            image = image_url
        )
        new_listing.save()

        # TODO: send user to the new page

    # send an empty form
    return render(request, "auctions/new_listing.html", {
        "form": NewListingForm()
    })

def listing(request, listing_id):
    
    if request.method == "POST":
        # TODO:
        pass

    all_bids = Bid.objects.filter(bid_on_id=listing_id)
    highest_bid_id = all_bids.order_by("value").first()
    if highest_bid_id:
        highest_bid = Bid.objects.get(bid_id = highest_bid_id)
    else:
        highest_bid = ""

    listed_by = Auction_listing.objects.get(id=listing_id).listed_by

    return render(request, "auctions/listing.html", {
        "listing": Auction_listing.objects.get(id=listing_id),
        "highest_bid": highest_bid,
        "num_bids": len(all_bids),
        "form": NewBidForm(),
        "listed_by": listed_by
    })

def categories(request):
    pass

def watchlist(request):
    pass

class NewListingForm(forms.Form):
    title = forms.CharField(max_length=64, required=True)
    description = forms.CharField(max_length=256, widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}))
    start_bid = forms.DecimalField(decimal_places=2, max_digits=16, required=True)
    image = forms.URLField(required=False)
    category = forms.CharField(max_length=64, required=False)

class NewBidForm(forms.Form):
    value = forms.DecimalField(decimal_places=2, max_digits=16, required=True)