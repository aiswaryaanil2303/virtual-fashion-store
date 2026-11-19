from django.db import models

# Create your models here.
import uuid
from django.db import models


# 1. Stores every clothing item & shoe in your store
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('top', 'Tops & Outerwear'),
        ('bottom', 'Bottoms'),
        ('shoes', 'Footwear'),
    ]

    slug = models.SlugField(unique=True)  # Short ID like 'r1', 'b1', 's1'
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='top')
    tag = models.CharField(max_length=30, blank=True, default='New')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    color_name = models.CharField(max_length=50, default='Black')
    color_hex = models.CharField(max_length=7, default='#1d1d20')
    image_filename = models.CharField(
        max_length=120,
        blank=True,
        help_text="Filename inside static/images/ (e.g., rack1-1.png, bottom(1).png)"
    )
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.color_name}) - ${self.price}"


# 2. Stores a customer's checkout order
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    city = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=20)
    promo_code = models.CharField(max_length=30, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically generate a unique order ID like TRD-4F91A2 before saving
        if not self.order_number:
            self.order_number = f"TRD-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} — {self.full_name} (${self.total})"


# 3. Stores each individual garment inside an Order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=120)
    variant = models.CharField(max_length=80)  # e.g. "Black (M)"
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} ({self.variant})"


# 4. Stores newsletter email signups from the Home page
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email