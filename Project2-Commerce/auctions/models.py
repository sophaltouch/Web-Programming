from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    pass
class Category(models.Model):
    # catId = models.PrimaryKey(max_length=)
    category = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.category}"
class Listing(models.Model):
    title = models.CharField(max_length=60)
    flActive = models.BooleanField(default=True)
    create_date = models.DateTimeField(default=now,blank=True)
    description = models.CharField(null=True, max_length=300)
    startingBid = models.FloatField()
    currentBid = models.FloatField(blank=True,null=True)
    category = models.ForeignKey(Category,null=True,blank=True,on_delete=models.CASCADE,related_name="similar_listing")
    creator = models.ForeignKey(User,on_delete=models.PROTECT,related_name="all_creator_listings")
    watchers = models.ManyToManyField(User,blank=True,related_name="watched_listings")
    buyer = models.ForeignKey(User,blank=True,null=True,on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.title} - {self.startingBid}"
class Bid(models.Model):
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.FloatField()
    date = models.DateTimeField(auto_now=True)
class Comment(models.Model):
    comment = models.CharField(max_length=100)
    createDate = models.DateTimeField(default=now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name="get_comment")
    
    def get_creation_date(self):
        return self.createDate.strftime('%B %d %Y')

class Picture(models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name="get_pictures")
    picture = models.ImageField(upload_to="static/images/")
    alt_text = models.CharField(max_length=140)