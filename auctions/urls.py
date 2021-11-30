from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing/<str:listing_id>", views.listing, name="listing"),
    path("categories", views.categories_list, name="categories"),
    path("categories/<str:category>", views.categories, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<str:listing_id>/comment", views.comment, name="comment"),
    path("listing/<str:listing_id>/watchlist", views.toggle_watchlist, name="toggle_watchlist")
]
