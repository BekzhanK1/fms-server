from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from users.managers import UserManager

class Role(models.TextChoices):
    Farmer = 'Farmer', _('Farmer')
    Buyer = 'Buyer', _('Buyer')
    Admin = 'Admin', _('Admin')
    

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.Buyer)
    avatar = models.ImageField(
        upload_to='avatars/', null=True, blank=True 
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

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