from django.db import models
from accounts.models import User
from vendors.models import FoodItem
from trains.models import Train, Station, Platform
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import transaction
from django.utils import timezone
import uuid

User = get_user_model()

class Station(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    region = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Train(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=20, unique=True)
    class_type = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.name} ({self.number})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('COD', 'Cash on Delivery'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    train = models.ForeignKey(Train, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_time = models.DateTimeField()
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]
    
    def get_payment_status_display(self):
        return dict(self.PAYMENT_STATUS_CHOICES)[self.payment_status]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.food_item.name}"

class PNROrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pnr_number = models.CharField(max_length=10, unique=True)
    train_number = models.CharField(max_length=10)
    train_name = models.CharField(max_length=100)
    from_station = models.CharField(max_length=100)
    to_station = models.CharField(max_length=100)
    journey_date = models.DateField()
    class_type = models.CharField(max_length=50)
    passenger_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PNR: {self.pnr_number} - {self.train_name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'PNR Order'
        verbose_name_plural = 'PNR Orders'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_total(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity}x {self.food_item.name}"
    
    @property
    def subtotal(self):
        return self.food_item.price * self.quantity
