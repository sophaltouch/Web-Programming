from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User,Category,Comment,Listing,Picture,Bid
from django.forms import ModelForm,modelformset_factory
from django import forms


class newCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment':forms.TextInput(attrs={'class':'form-control','placeholder':'leave your comment here'})
        }
def activeListings(request):
    category = request.GET.get("Category",None)
    categories = Category.objects.all()
    if category is None:
        listings = Listing.objects.filter(flActive=True)
    else:
        listings = Listing.objects.filter(flActive=True,category=category_id)
        
    for listing in listings:
        listing.mainPicture = listing.get_pictures.first()
        if request.user in listing.watchers.all():
            listing.is_watched = True
        else:
            listing.is_watched = False
        return render(request,"auctions\index.html",{
        "listings":listings,
        "categories":Category.objects.all(),
        "page_title":"Active Listings"
        })

def index(request):
    return render(request,"auctions\index.html")

# def Category(request,category,user):
#     category_name = Category.objects.get(name=category)
#     user_name = User.objects.get(user=username)
#     list = Listing.objects.filter(category=category_name,user = user_name).order_by('id').reverse()
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse('login'))
#     else:
#         return render(request,"auctions/category.html")

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

# def listing(request,listing_id):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse('login'))
    
#     listing = Listing.objects.get(id=listing_id)
#     if request.user in listing.watchers.all():
#         listing.is_watched = True
#     else:
#         lising.is_watched = False
#     return render(request,"auctions\listing.html",{
#         "listing":listing,
#         "listing_picture":listing.get_pictures.all(),
#         "form":newBidForm(),
#         "comment":listing.get_comment.all(),
#         "comment_form":newcommentForm()
#     })


# def close_listing(request,listing_id):
#     listing = Listing.objects.get( id=listing_id )
#     if request.user == listing.creator:
#         listing.flActive = False
#         listing.buyer = Bid.objects.filter(auction=listing).last().user
#         listing.save()
#         return HttpResponseRedirect(reverse("listing",args=[listing_id]))
#     else:
#         listing.watchers.add(request.user)
#         return HttpResponseRedirect(reverse("watchlist"))

class newBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['offer']
# @login_required 
# def take_bid(request, listing_id):
#     listing = Listing.objects.get(id=listing_id)
#     offer = float(request.POST['offer'])
#     if is_valid(offer,listing):
#         listing.currentBid = offer
#         form = newBidForm(request.POST)
#         newBid = form.save(commit = False)
#         newBid.auction = lisiting 
#         newBid.user = request.user
#         newBid.save()
#         listing.save()
#         return HttpResponseRedirect(reverse('listing',args=[listing_id]))
#     else:
#         return render(request,"auction/listing.html",{
#             "listing":listing,
#             "listing_picture":listing.get_pictures.all(),
#             "form":newBidForm(),
#             "error_min_value":True
#         })

class newListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title','description','startingBid','category']
class newPictureForm(ModelForm):
    class Meta:
        model = Picture
        fields = ['picture','alt_text']
@login_required
def newListing(request):
    PictureFormSet = modelformset_factory(Picture,form=newPictureForm,extra=4)
    if request.method == "POST":
        form = newListingForm(request.POST,request.FILES)
        imagesForm = PictureFormSet(request.POST,request.FILES, queryset=Picture.objects.none())
        if form.is_valid() and imagesForm.is_valid():
            newListing = form.save(commit = False)
            newListing.creator = request.user 
            newListing.save()

            for form in imagesForm.cleaned_data:
                if form:
                    picture = form['picture']
                    text = form['alt_text']
                    newPicture = Picture(listing = newListing, picture=picture, alt_text=text)
                    newPicture.save()
            return render(request,"auctions\newListing.html",{
            "form":newListingForm(),
                "imageForm":PictureFormSet(queryset=Picture.objects.none()),
                "success":"Save Successful"
            })
        else:
            return render(request,"auctions\newListing.html",{
                "form":newListingForm(),
                "imageForm":PictureFormSet(queryset=Picture.objects.none())
            })
    else:
        return render(request,"auctions\newListing.html",{
            "form":newListingForm(),
            "imageForm":PictureFormSet(queryset=Picture.objects.none())
        })        
