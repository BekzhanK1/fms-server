from django.test import TestCase
from users.models import User
from .models import Farm, Application


class FarmApplicationTestCase(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            email="farmer@example.com", password="password123", role="Farmer"
        )

    def test_application_created_on_farm_creation(self):
        farm = Farm.objects.create(
            farmer=self.farmer,
            name="Test Farm",
            address="123 Green Lane",
            geo_loc="45.12345, -93.12345",
            size="20 acres",
            crop_types="Corn",
        )
        application = Application.objects.get(farm=farm)
        self.assertEqual(application.farmer, self.farmer)
        self.assertEqual(application.status, "pending")
