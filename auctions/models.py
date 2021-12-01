from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import CharField, related


class User(AbstractUser):
    pass

class Auction_listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.DecimalField(decimal_places=2, max_digits=16)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="provider")
    category = models.CharField(max_length=64)
    image = models.URLField()
    is_open_for_bids = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}: {self.description}"

class Watchlist(models.Model):
    watchlisted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlister")
    watchlisted_item = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, related_name="item")

    def __str__(self):
        return f"{self.item} watchlisted by {self.watchlisted_by}"

class Bid(models.Model):
    value = models.DecimalField(decimal_places=2, max_digits=16)
    by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid_on = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, related_name="listed")

    def __str__(self):
        return f"{self.value} bid by {self.by}"

class Comment(models.Model):
    on = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, related_name="listing")
    by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    comment = models.TextField()

    def __str__(self):
        return f"{self.comment} by {self.by} on {self.on}"
