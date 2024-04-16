from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.templatetags.static import static
# Create your models here.




class User(AbstractUser):
    address = models.TextField(default = 'No address')
class Car(models.Model):
    name = models.CharField(max_length = 100)
    description = models.TextField()
    image = models.ImageField()
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    category = models.ManyToManyField('Category', related_name = 'cars')


    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name
    
class CartItem(models.Model):
    product = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default = 0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

class OrderItem(models.Model):
    product = models.ForeignKey(Car, on_delete=models.CASCADE)    
    quantity = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    is_ordered = models.BooleanField(default = True)   
 
    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

class Order(models.Model):
    order_items = models.ManyToManyField('OrderItem', related_name = 'item')
    total_price = models.DecimalField(max_digits = 11, decimal_places = 2, default = 0.00)
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    date_added = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default = False)
 
    def __str__(self):
        return f'{self.date_added}'



class Profile(models.Model):
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_CHOICES = [
        (GENDER_MALE, _("Male")),
        (GENDER_FEMALE, _("Female")),
    ]
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to="profile_photos", null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=32, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    zip = models.CharField(max_length=30, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username