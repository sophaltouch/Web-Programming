from django.urls import path

from . import views

urlpatterns = [
    path("",views.index,name="index"),
    path("auctions/active",views.activelistings,name="activelist"),
    path("auctions/active/<int:category_id>",views.activelistings,name="activelist"),
    path("listing/<int:listing_id>",views.listing, name="listing"),
    path("close_list/<int:listing_id>",views.close_listing, name="close_list"),
    path("comment/<int:listing_id>",views.comment,name="comment"),
    path("watchlist",views.watchlist, name="watchlist"),
    path("change_watchlist/<int:listing_id>/<str:revers>",views.change_watchlist,name="change_watchlist"),
    path("take_bid/<int:listing_id>", views.take_bid, name="take_bid"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("category", views.Category, name="category"),
    path("auctions/new", views.newListing, name="newlist"),
    
]