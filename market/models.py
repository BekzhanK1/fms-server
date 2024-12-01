from django.db import models
from farms.models import Farm
from users.models import User


class OrderStatus(models.TextChoices):
    Pending = ("pending", "Pending")
    Processing = ("processing", "Processing")
    Completed = ("completed", "Completed")
    Canceled = ("cancelled", "Cancelled")


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.description}"


class Product(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="products", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def decrease_stock(self, quantity):
        if self.stock_quantity < quantity:
            raise ValueError("Not enough stock")
        self.stock_quantity -= quantity
        self.save()

    def __str__(self):
        return f"{self.name} - {self.farm.name} - {self.price}"


class Basket(models.Model):
    buyer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="basket",
        limit_choices_to={"role": "Buyer"},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.email} - {self.created_at}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    def clear(self):
        self.items.all().delete()


class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items")
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - Qty: {self.quantity}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        limit_choices_to={"role": "Buyer"},
    )
    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="orders", null=True, blank=True
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=OrderStatus.choices, default=OrderStatus.Pending
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Date: {self.created_at} | Order {self.id} - Buyer: {self.buyer.email} - Status: {self.status} - Total: {self.total_price}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - Qty: {self.quantity}"
