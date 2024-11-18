from users.models import BuyerInfo, FarmerInfo, User


def create_if_not_exists(user: User):
    if user.role == "Farmer":
        FarmerInfo.objects.get_or_create(farmer=user)
    elif user.role == "Buyer":
        BuyerInfo.objects.get_or_create(buyer=user)
    else:
        raise ValueError("Invalid role")
