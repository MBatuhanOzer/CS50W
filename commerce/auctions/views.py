from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from .models import User, Category, Listing, Comment, Bid


def index(request):
    categories = Category.objects.all()
    activeListings = Listing.objects.filter(activeness=True)
    return render(request, "auctions/index.html",{
        "listings": activeListings,
        "categories": categories,
        "title": "Active Listings"
    })

@login_required(login_url="/login", redirect_field_name=None)
def create(request):
    if request.method == "POST":
            title = request.POST.get("title", None)
            description = request.POST.get("description", None)
            image = request.POST.get("image-path", None)
            try:
                price = float(request.POST.get("price", None))
                if price < 0:
                    return HttpResponseRedirect(reverse("create"))
            except ValueError:
                return HttpResponseRedirect(reverse("create"))
            category = request.POST.get("category", None)
            if category != None:
                try:
                    category = Category.objects.get(catname=category)
                except ObjectDoesNotExist:
                    return HttpResponseRedirect(reverse("create"))
            user = request.user
            if title == None or description == None or price == None:
                return HttpResponseRedirect(reverse("create"))
            else:
                newlisting = Listing(
                    title=title,
                    description=description,
                    imagelink=image,
                    owner=user,
                    category=category
                )
                newlisting.save()
                newbid = Bid(
                    bid=price,
                    user=user,
                    listing=newlisting
                )
                newbid.save()
                return HttpResponseRedirect(reverse("index"))
    else:
        categories = Category.objects.all()
        return render(request, "auctions/create.html",{
            "categories": categories
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

@login_required(login_url="/login", redirect_field_name=None)
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

def category(request):
    catname = request.GET.get("category", None)
    if catname == None:
        return HttpResponseRedirect(reverse("index"))
    try:
        category = Category.objects.get(catname=catname)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("index"))
    categories = Category.objects.all()
    activeListings = Listing.objects.filter(activeness=True, category=category)
    return render(request, "auctions/index.html",{
        "listings": activeListings,
        "categories": categories,
        "catname": catname,
    })

def listing(request, id):
    if request.method == "POST":
        try:
            details = Listing.objects.get(pk=id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("index"))
        if request.POST.get("close", None):
            details.activeness = False
            details.watchlist.clear()
            details.save()
        if request.POST.get("open", None):
            details.activeness = True
            details.save()
        return HttpResponseRedirect(reverse("listing", args=(id,)))
    else:
        try:
            details = Listing.objects.get(pk=id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("index"))
        watchlist = details.watchlist.filter(id=request.user.id).exists()
        max = details.price.all().aggregate(Max("bid"))
        biduser = details.price.filter(bid=max["bid__max"]).first()
        currentuser = False
        if biduser.user == request.user:
            currentuser = True
        owner = False
        if details.owner == request.user:
            owner = True
        biddetails = {"count": details.price.count(), "current":max}
        return render(request, "auctions/listing.html", {
            "listing": details,
            "watchlist": watchlist,
            "bid": biddetails,
            "currentuser": currentuser,
            "owner": owner
        })

@login_required(login_url="/login", redirect_field_name=None)
def handlewatchlist(request, id):
    if request.method == "POST":
        try:
            details = Listing.objects.get(pk=id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("index"))
        user = request.user
        if details.watchlist.filter(id=user.id).exists():
            details.watchlist.remove(user)
        else:
            details.watchlist.add(user)
        return HttpResponseRedirect(reverse("listing", args=(id,)))
    return HttpResponseRedirect(reverse("listing", args=(id,)))

@login_required(login_url="/login", redirect_field_name=None)
def watchlist(request):
    user = request.user
    watchlist = user.inwatch.all()
    return render(request, "auctions/index.html",{
        "listings": watchlist,
        "title": "Watchlist"
    })

@login_required(login_url="/login", redirect_field_name=None)
def comment(request, id):
    if request.method == "POST":
        try:
            details = Listing.objects.get(pk=id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("index"))
        user = request.user
        comment = request.POST.get("comment", None)
        if comment == None or len(comment) > 500:
            return HttpResponseRedirect(reverse("index"))
        new = Comment(
            owner= user,
            listing = details,
            text = comment
        )
        new.save()
        return HttpResponseRedirect(reverse("listing", args=(id,)))
    return HttpResponseRedirect(reverse("index"))

@login_required(login_url="/login", redirect_field_name=None)
def bid(request, id):
    if request.method == "POST":
        try:
            details = Listing.objects.get(pk=id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("index"))
        try:
            price = float(request.POST.get("price", None))
            if price < 0:
                return HttpResponseRedirect(reverse("index"))
        except ValueError:
            return HttpResponseRedirect(reverse("index"))
        for bid in details.price.all():
            if price <= bid.bid:
                return HttpResponseRedirect(reverse("index"))
        user = request.user
        newbid = Bid(
            bid=price,
            user=user,
            listing=details
        )
        newbid.save()
        return HttpResponseRedirect(reverse("listing", args=(id,)))
