from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Car)
admin.site.register(Brand)
admin.site.register(FuelType)
admin.site.register(Performance)
admin.site.register(Engine)
admin.site.register(TagCategory)
admin.site.register(Tag)
