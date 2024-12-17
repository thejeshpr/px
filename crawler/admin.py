from django.contrib import admin
from .models import SiteConf, Category

@admin.register(SiteConf)
class SiteConfAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url', 'category', 'enabled', 'is_locked', 'ns_flag', 'scraper_name', 'updated_at')
    list_filter = ('enabled', 'is_locked', 'ns_flag', 'category', 'updated_at')
    search_fields = ('name', 'base_url', 'scraper_name', 'slug', 'notes')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ("General Info", {
            'fields': ('name', 'slug', 'category', 'base_url', 'icon', 'scraper_name', 'notes')
        }),
        ("Status and Flags", {
            'fields': ('enabled', 'is_locked', 'ns_flag')
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at')
        }),
        ("Advanced Options", {
            'fields': ('extra_data_json',)
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)