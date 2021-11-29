from django.contrib import admin
from .models import Auction_listing, Bid, Comment, User

# Register your models here.
admin.site.register(User)
admin.site.register(Auction_listing)
admin.site.register(Bid)
admin.site.register(Comment)