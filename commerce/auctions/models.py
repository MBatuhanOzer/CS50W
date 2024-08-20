from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    catname = models.CharField(max_length=32)

    def __str__(self):
        return self.catname


class Listing(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    imagelink = models.CharField(max_length=128, blank=True, null=True)
    activeness = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="inwatch")

class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment")
    text = models.CharField(max_length=500)


class Bid(models.Model):
    bid = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="price")

    def __str__(self):
        return str(self.bid)
