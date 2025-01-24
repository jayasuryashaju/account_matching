from django.contrib import admin
from .models import RawData

# Register the RawData model in the admin interface
@admin.register(RawData)
class RawDataAdmin(admin.ModelAdmin):
    list_display = ('distributor_name','retailer_name', 'item_description', 'street', 'city', 'state', 'zip_code')  # Columns to display in the list view
    search_fields = ('retailer_name', 'street', 'city', 'state', 'zip_code')  # Fields to search by in the admin panel
    list_filter = ('state',)  # Optional: Filter by state in the admin panel
    ordering = ('retailer_name',)  # Default ordering of records in the admin panel
