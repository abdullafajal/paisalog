from django.contrib import admin
from .models import Category, Entry

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'updated_at')
    list_filter = ('user',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'entry_type', 'category', 'amount', 'amount_type', 'user')
    list_filter = ('entry_type', 'amount_type', 'user', 'date')
    search_fields = ('description', 'category__name')
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')
