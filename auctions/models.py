from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import CharField, related


class User(AbstractUser):
    pass

class Auction_listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.DecimalField(decimal_places=2)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="provider")
    category = models.CharField(max_length=64)
    image = models.URLField()

class Bid(models.Model):
    value = models.DecimalField(decimal_places=2)
    by = models.ForeignKey(User, related_name="bidder")
    bid_on = models.ForeignKey(Auction_listing, )

class Comment(models.Model):
    on = models.ForeignKey(Auction_listing, related_name="listing")
    by = models.ForeignKey(User, related_name="commenter")
    comment = models.TextField()
