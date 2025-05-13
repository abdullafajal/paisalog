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
    list_display = ('get_entry_date', 'get_entry_type', 'get_category', 'get_amount', 'get_amount_type', 'get_user')
    list_filter = ('entry_type', 'amount_type', 'user', 'date')
    search_fields = ('description', 'category__name')
    ordering = ('-date', '-created_at')

    def get_queryset(self, request):
        """Override the default queryset to handle potential database issues"""
        try:
            queryset = super().get_queryset(request)
            # Avoid complex queries that might cause SQLite issues
            return queryset.select_related('category', 'user')
        except Exception as e:
            # Return an empty queryset if there's an issue
            return Entry.objects.none()

    def get_entry_date(self, obj):
        try:
            return obj.date
        except Exception:
            return None
    get_entry_date.short_description = 'Date'
    get_entry_date.admin_order_field = 'date'

    def get_entry_type(self, obj):
        try:
            return obj.entry_type
        except Exception:
            return None
    get_entry_type.short_description = 'Entry Type'
    get_entry_type.admin_order_field = 'entry_type'

    def get_category(self, obj):
        try:
            return obj.category
        except Exception:
            return None
    get_category.short_description = 'Category'
    get_category.admin_order_field = 'category'

    def get_amount(self, obj):
        try:
            return obj.amount
        except Exception:
            return None
    get_amount.short_description = 'Amount'
    get_amount.admin_order_field = 'amount'

    def get_amount_type(self, obj):
        try:
            return obj.amount_type
        except Exception:
            return None
    get_amount_type.short_description = 'Amount Type'
    get_amount_type.admin_order_field = 'amount_type'

    def get_user(self, obj):
        try:
            return obj.user
        except Exception:
            return None
    get_user.short_description = 'User'
    get_user.admin_order_field = 'user'
