from django.contrib import admin
from .models import UrlModel

@admin.register(UrlModel)
class UrlModelAdmin(admin.ModelAdmin):
    list_display = ['url', 'short_code', 'created_at', 'updated_at', 'access_count']
    search_fields = ('short_code', 'url')

