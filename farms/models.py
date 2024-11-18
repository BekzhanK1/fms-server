from django.db import models
from django.utils import timezone
from users.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class Farm(models.Model):
    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="farms",
        limit_choices_to={"role": "Farmer"},
    )
    name = models.CharField(max_length=255)
    address = models.TextField()
    geo_loc = models.CharField(max_length=255)
    size = models.CharField(max_length=50)
    crop_types = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.farmer.email}"


class Application(models.Model):
    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications",
        limit_choices_to={"role": "Farmer"},
    )
    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(
        max_length=10,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
    )
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Application {self.id} - Farmer: {self.farmer.email} - Status: {self.status}"


@receiver(post_save, sender=Farm)
def create_application_for_farm(sender, instance, created, **kwargs):
    if created:
        Application.objects.create(farmer=instance.farmer, farm=instance)
