from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import exceptions
from django.db import IntegrityError
from django.db.models.aggregates import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import BadHeaderError
from django.shortcuts import render
from django.urls import reverse
from .models import User,Category,Comment,Listing,Picture,Bid
from django.forms import ModelForm,modelformset_factory,widgets
from django import forms

class newBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['offer']
class newCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment':forms.TextInput(attrs={'label':'lb_comment','class':'form-control','placeholder':'leave your comment','aria-describedby':'basic-addon1'})
        }
def index(request):
    return activelistings(request)
    
def activelistings(request):
    category_id = request.GET.get("category", None)
    if category_id is None:
        listings = Listing.objects.filter(flActive=True).order_by('id').reverse()
    else:
        listings = Listing.objects.filter(flActive=True,category=category_id).order_by('id').reverse()
    for listing in listings:
        listing.mainPicture = listing.get_pictures.first()
        if request.user in listing.watchers.all():
            listing.is_watched = True   
        else:
            listing.is_watched = False 
    if not request.user.is_authenticated:
        return render(request,"auctions/index.html",{
        "list":listings,
        "categories":Category.objects.all(),
        "page_title":"Active Listings",
        })
    else:
        list = request.user.watched_listings.all() 
        totalwatch = list.count()
        return render(request,"auctions/index.html",{
        "list":listings,
        "categories":Category.objects.all(),
        "page_title":"Active Listings",
        "totalwatch":totalwatch,
        })

def listing(request,listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse(login_view))
    listing = Listing.objects.get(id=listing_id)
    listings = request.user.watched_listings.all()
    totalwatch = listings.count()
    if request.user in listing.watchers.all():
        listing.is_watched = True    
    else:
        listing.is_watched = False
    return render(request,"auctions\listing.html",{
        "list":listing,
        "listing_picture":listing.get_pictures.all(),
        "form":newBidForm(),
        "comment":listing.get_comment.all(),
        "comment_form":newCommentForm(),
        "totalwatch":totalwatch,
        "categories":Category.objects.all()
    })

def close_listing(request,listing_id):
    listing = Listing.objects.get(id = listing_id)
    if request.user == listing.creator:
        listing.flActive = False
        listing.buyer = Bid.objects.filter(auction=listing).last().user
        listing.save()
        return HttpResponseRedirect(reverse("listing",args=[listing_id]))
    else:
        listing.watchers.add(request.user)
        return HttpResponseRedirect(reverse("watchlist"))
@login_required
def comment(request,listing_id):
    listing = Listing.objects.get(id=listing_id)
    form = newCommentForm(request.POST)
    newComment = form.save(commit = False)
    newComment.user = request.user
    newComment.listing = listing
    newComment.save()
    return HttpResponseRedirect(reverse("listing",args=[listing_id]))
@login_required
def watchlist(request):
    listings = request.user.watched_listings.all().order_by('id').reverse()
    totalwatch = listings.count()
    for listing in listings:
        listing.mainPicture = listing.get_pictures.first()
        if request.user in listing.watchers.all():
            listing.is_watched = True   
        else:
            listing.is_watched = False 
    if request.user.is_authenticated:
        return render(request,"auctions/index.html",{
        "list":listings,
        "page_title":"WatchList",
        "categories":Category.objects.all(),
        "totalwatch":totalwatch
        })
    else:
        return HttpResponseRedirect(reverse(index))
    

@login_required
def change_watchlist(request,listing_id,revers):
    listing_obj = Listing.objects.get(id = listing_id)
    if request.user in listing_obj.watchers.all():
        listing_obj.watchers.remove(request.user)
        return listing(request,listing_id)
    else:
        listing_obj.watchers.add(request.user)
    if revers == "listing":
        return listing(request,listing_id)
    else:
        return HttpResponseRedirect(reverse(revers))

class newListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title','description','startingBid','category']
        widgets={
            'title':forms.TextInput(attrs={'label':'a','class':'form-control','placeholder':'Title','aria-describedby':'basic-addon1'}),
            'description':forms.Textarea(attrs={'label':'','class':'form-control','placeholder':'Description'}),
        }
class newPictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ['picture','alt_text']
        widgets={
            'alt_text':forms.TextInput(attrs={'class':'form-control','placeholder':'input-alt-text'})
        }

@login_required
def newListing(request):
    PictureFormSet = modelformset_factory(Picture,form=newPictureForm,extra=1)
    if request.method == "POST":
        form = newListingForm(request.POST,request.FILES)
        imagesForm = PictureFormSet(request.POST,request.FILES, queryset=Picture.objects.none())
        if form.is_valid() and imagesForm.is_valid():
            newListing = form.save(commit = False)
            newListing.creator = request.user 
            newListing.save()
            for form in imagesForm.cleaned_data:
                    if form:
                        pictures = form['picture']
                        text = form['alt_text']
                        newPicture = Picture(listing=newListing, picture=pictures, alt_text=text)
                        newPicture.save()                
                    return render(request,"auctions/newListing.html",{
                    "form":newListingForm(),
                    "imageForm": PictureFormSet(queryset=Picture.objects.none()),
                    "categories":Category.objects.all(),
                    "success":True
                    })
        
        else:
            return render(request,"auctions/newListing.html",{
                "form":newListingForm(),    
                "imageForm": PictureFormSet(queryset=Picture.objects.none()),
                "categories":Category.objects.all(),
                "false":True 
            })
    else:
        return render(request,"auctions/newListing.html",{
            "form":newListingForm(),
            "imageForm": PictureFormSet(queryset=Picture.objects.none()),
            "categories":Category.objects.all(),
        })

def is_valid(offer,listing):
    if offer >= listing.startingBid and (listing.currentBid is None or offer > listing.currentBid):
        return True
    else: 
       return False

@login_required
def take_bid(request, listing_id):
    listing = Listing.objects.get(id = listing_id)
    offer = float(request.POST['offer'])
    if is_valid(offer, listing):
        listing.currentBid = offer
        form = newBidForm(request.POST)
        newBid = form.save(commit=False)
        newBid.auction = listing 
        newBid.user = request.user
        newBid.save()
        listing.save()
        return HttpResponseRedirect(reverse("listing",args=[listing_id]))
    else:
        return render(request, "auctions/listing.html",{
            "list":listing,
            "listing_picture":listing.get_pictures.all(),
            "form":newBidForm(),
            "error_min_value":True,
            "comment":listing.get_comment.all(),
            "comment_form":newCommentForm(),
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


