from django.contrib import admin
from .models import VRCard

class VRCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'link')  # Define los campos que deseas mostrar en la lista

admin.site.register(VRCard, VRCardAdmin)


