from django.db import models
from django.utils.translation import gettext_lazy as _


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
