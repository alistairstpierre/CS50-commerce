from turtle import title
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    imageURL = models.URLField()
    category = models.CharField(max_length=50)
    current_bid = models.DecimalField(max_digits=9, decimal_places=2)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    winner_id = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.id} {self.username}: {self.title} {self.category} {self.current_bid}"

class Watchlist(models.Model):
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.auction_id} {self.username}"

class Bid(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.auction_id} {self.username} {self.amount}"
    
class Comment(models.Model):
    comment = models.CharField(max_length=1000)
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.auction_id} {self.username} {self.comment}"


class Category(models.Model):
    Books = "Books"
    BusinessAndIndustrial = "Business & Industrial"
    ClothingAndShoesAndAccessories = "Clothing, Shoes & Accessories"
    Collectibles = "Collectibles"
    ConsumerElectronics ="Consumer Electronics"
    Crafts = "Crafts"
    DollsAndBears = "Dolls & Bears"
    HomeAndGarden = "Home & Garden"
    Motors = "Motors"
    PetSupplies = "Pet Supplies"
    SportingGoods = "Sporting Goods"
    SportsMemAndCardsAndFanShop = "Sports Mem, Cards & Fan Shop"
    ToysAndHobbies = "Toys & Hobbies"
    Antiques = "Antiques"
    ComputersAndTabletsAndNetworking = "Computers/Tablets & Networking"
    category_choices = [
        (Books, Books),
        (BusinessAndIndustrial, BusinessAndIndustrial),
        (ClothingAndShoesAndAccessories, ClothingAndShoesAndAccessories),
        (Collectibles, Collectibles),
        (ConsumerElectronics, ConsumerElectronics),
        (Crafts, Crafts),
        (DollsAndBears, DollsAndBears),
        (HomeAndGarden, HomeAndGarden),
        (Motors, Motors),
        (PetSupplies, PetSupplies),
        (SportingGoods, SportingGoods),
        (SportsMemAndCardsAndFanShop, SportsMemAndCardsAndFanShop),
        (ToysAndHobbies, ToysAndHobbies),
        (Antiques, Antiques),
        (ComputersAndTabletsAndNetworking, ComputersAndTabletsAndNetworking)
    ]