from typing_extensions import Required
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Auction_listing, Bid, Comment, Watchlist


def index(request):
    # get all the highest bids
    highest_bids = []
    highest_bids_ids = []
    for listing in Auction_listing.objects.filter():
        high_bid = Bid.objects.filter(bid_on_id=listing.id).order_by("value").last()
        if high_bid:
            highest_bids.append(high_bid)
            highest_bids_ids.append(high_bid.bid_on_id)

    return render(request, "auctions/index.html", {
        "listings": Auction_listing.objects.filter(),
        "highest_bids": highest_bids,
        "highest_bids_ids": highest_bids_ids
    })


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

        # send user to the new page
        return HttpResponseRedirect(reverse("listing", args=(str(new_listing.id))))

    # send an empty form
    return render(request, "auctions/new_listing.html", {
        "form": NewListingForm()
    })

def listing(request, listing_id):
    # first get some data
    all_bids = Bid.objects.filter(bid_on_id=listing_id)
    highest_bid= all_bids.order_by("value").last()
    
    listed_by = Auction_listing.objects.get(id=listing_id).listed_by
    errormessage = ""

    comments = Comment.objects.filter(on_id=listing_id)
    
    if request.method == "POST":
        new_bid_value = request.POST["value"]

        # if the bid is too low, send an error message
        if highest_bid:
            current_bid = highest_bid.value
        else:
            current_bid = Auction_listing.objects.get(id=listing_id).start_bid

        if float(new_bid_value) < float(current_bid):
            errormessage = "A bid must be higher than the previous bid and higher than the starting bid"
            return render(request, "auctions/listing.html", {
                "listing": Auction_listing.objects.get(id=listing_id),
                "highest_bid": highest_bid,
                "num_bids": len(all_bids),
                "form": NewBidForm(),
                "listed_by": listed_by,
                "errormessage": errormessage,
                "form_comment": NewCommentForm(),
                "comments": comments
            })
        
        else:
            # the bid is valid, so add it to this listing
            new_bid = Bid(
                value = new_bid_value,
                by = User.objects.get(pk=request.user.id),
                bid_on = Auction_listing.objects.get(id=listing_id)
            )

            new_bid.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id)))

    return render(request, "auctions/listing.html", {
        "listing": Auction_listing.objects.get(id=listing_id),
        "highest_bid": highest_bid,
        "num_bids": len(all_bids),
        "form": NewBidForm(),
        "listed_by": listed_by,
        "form_comment": NewCommentForm(),
        "comments": comments
    })

def comment(request, listing_id):
    if request.method == "POST":
        # add the comment to the database
        writer = request.user
        text = request.POST["text"]

        new_comment = Comment(
            on=Auction_listing.objects.get(id=listing_id),
            by=writer,
            comment=text
        )

        new_comment.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id)))

def watchlist(request):
    highest_bids = []
    for listing in Auction_listing.objects.filter():
        highest_bids.append(Bid.objects.filter(bid_on_id=listing.id).order_by("value").last())

    # send the listings that are on the watchlist
    listings = Watchlist.objects.filter(watchlisted_by_id=request.user.id)

    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "highest_bids": highest_bids
    })

def toggle_watchlist(request, listing_id):
    if request.method == "POST":
        if Watchlist.objects.filter(watchlisted_item_id=listing_id).filter(watchlisted_by_id=request.user.id):
            # the user want to toggle it off
            Watchlist.objects.filter(watchlisted_item_id=listing_id).filter(watchlisted_by_id=request.user.id).delete()
        else:
            # the user wants to toggle it on
            new_watchlist = Watchlist(
                watchlisted_by=request.user,
                watchlisted_item=Auction_listing.objects.get(id=listing_id)
            )
            new_watchlist.save()

    return HttpResponseRedirect(reverse("listing", args=(listing_id)))

def close(request, listing_id):
    if request.method == "POST":
        # check if the user is authorized to close the bidding
        if request.user == Auction_listing.objects.get(id=listing_id).listed_by:
            listing = Auction_listing.objects.get(id=listing_id)
            listing.is_open_for_bids = False
            listing.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id)))

def categories_list(request):
    cats = set()
    for listing in Auction_listing.objects.filter():
        cats.add(listing.category)
    
    return render(request, "auctions/categories_list.html", {
        "categories": cats
    })

def categories(request, category):
    # give a list with all listings that have this category
    listings = []
    highest_bids = []
    highest_bids_ids = []
    for listing in Auction_listing.objects.filter():
        high_bid = Bid.objects.filter(bid_on_id=listing.id).order_by("value").last()
        if high_bid:
            highest_bids.append(high_bid)
            highest_bids_ids.append(high_bid.bid_on_id)
        if listing.category == category:
            listings.append(listing)

    return render(request, "auctions/categories.html", {
        "listings": listings,
        "category": category,
        "highest_bids": highest_bids,
        "highest_bids_ids": highest_bids_ids
    })

class NewListingForm(forms.Form):
    title = forms.CharField(max_length=64, required=True)
    description = forms.CharField(max_length=256, widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}))
    start_bid = forms.DecimalField(decimal_places=2, max_digits=16, required=True)
    image = forms.URLField(required=False)
    category = forms.CharField(max_length=64, required=False)

class NewBidForm(forms.Form):
    value = forms.DecimalField(decimal_places=2, max_digits=16, required=True)

class NewCommentForm(forms.Form):
    text = forms.CharField(max_length=256, required=True)
