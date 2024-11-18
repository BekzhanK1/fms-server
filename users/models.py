from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator

from users.managers import UserManager


class Role(models.TextChoices):
    Farmer = "Farmer", _("Farmer")
    Buyer = "Buyer", _("Buyer")
    Admin = "Admin", _("Admin")


class PaymentMethod(models.TextChoices):
    Cash = "Cash", _("Cash")
    Card = "Card", _("Card")
    QR = "QR", _("QR")


class SocialType(models.TextChoices):
    Facebook = "Facebook", _("Facebook")
    Twitter = "Twitter", _("Twitter")
    Instagram = "Instagram", _("Instagram")
    LinkedIn = "LinkedIn", _("LinkedIn")


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.Buyer)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_farmer(self):
        return self.role == Role.Farmer

    @property
    def is_buyer(self):
        return self.role == Role.Buyer

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def switch_role(self):
        if self.role == Role.Admin:
            raise ValueError("Admin role cannot be switched")
        elif self.role == Role.Buyer:
            self.role = Role.Farmer
            self.save()
        elif self.role == Role.Farmer:
            self.role = Role.Buyer
            self.save()
        else:
            raise ValueError("Invalid role")

    def __str__(self):
        return f"{self.email} - {self.role}"


class FarmerInfo(models.Model):
    farmer = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="farmer_info"
    )
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], default=0.0
    )
    experience = models.PositiveSmallIntegerField(default=0)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"FarmerInfo: {self.farmer.email} - Rating: {self.rating}"


class BuyerInfo(models.Model):
    buyer = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="buyer_info"
    )
    delivery_address = models.TextField(blank=True, null=True)
    payment_method = models.CharField(
        max_length=50, choices=PaymentMethod.choices, default=PaymentMethod.Cash
    )

    def __str__(self):
        return f"BuyerInfo: {self.buyer.email} - Payment Method: {self.payment_method}"


class Social(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, choices=SocialType.choices)
    url = models.URLField()

    def __str__(self):
        return f"Social: {self.farmer.email} - {self.platform}"
