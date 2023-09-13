from django.contrib import admin
from .models import VRCard,Tarjeta

class VRCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'link')  # Define los campos que deseas mostrar en la lista

admin.site.register(VRCard, VRCardAdmin)


class TarjetaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'enlace')  # Campos que se mostrarán en la lista de tarjetas
    search_fields = ('titulo',)  # Campos que se pueden buscar

admin.site.register(Tarjeta, TarjetaAdmin)