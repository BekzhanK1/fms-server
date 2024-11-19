from market.models import Basket
from users.models import BuyerInfo, FarmerInfo, User


def create_if_not_exists(user: User):

    if user.role == "Farmer" or user.role == "Buyer":
        FarmerInfo.objects.get_or_create(farmer=user)
        BuyerInfo.objects.get_or_create(buyer=user)
        Basket.objects.get_or_create(buyer=user)
    else:
        raise ValueError("Invalid role")
