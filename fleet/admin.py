from django.contrib import admin

from .models import FishType, FisherMan, Ship, Fish, Net

admin.site.register(Ship)
admin.site.register(FishType)
admin.site.register(FisherMan)
admin.site.register(Fish)
admin.site.register(Net)
