from django.contrib import admin

from users.models import BuyerInfo, FarmerInfo, User

admin.site.register(User)
admin.site.register(BuyerInfo)
admin.site.register(FarmerInfo)
