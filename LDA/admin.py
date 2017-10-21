from __future__ import unicode_literals
from .models import Transformer, Building, Connection, User
from django.contrib import admin

class TransformerAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'kVA')

class ConnectionAdmin(admin.ModelAdmin):
	list_display = ('Transformer', 'Building')

# Register your models here.
admin.site.register(Building)
admin.site.register(Transformer, TransformerAdmin)
admin.site.register(Connection, ConnectionAdmin)
admin.site.register(User)
