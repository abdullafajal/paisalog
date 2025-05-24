import django_filters
from django import forms
from django.utils import timezone
from datetime import datetime, time
from .models import Entry

class EntryFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        label='From Date',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        method='filter_date_from'
    )
    date_to = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        label='To Date',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        method='filter_date_to'
    )
    amount_min = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        label='Min Amount',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min'})
    )
    amount_max = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        label='Max Amount',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max'})
    )

    class Meta:
        model = Entry
        fields = {
            'entry_type': ['exact'],
            'category': ['exact'],
            'amount_type': ['exact'],
            'description': ['icontains'],
        }
    
    def filter_date_from(self, queryset, name, value):
        # Convert date to datetime at the start of the day with timezone
        start_of_day = timezone.make_aware(datetime.combine(value, time.min))
        return queryset.filter(date__gte=start_of_day)
    
    def filter_date_to(self, queryset, name, value):
        # Convert date to datetime at the end of the day with timezone
        end_of_day = timezone.make_aware(datetime.combine(value, time.max))
        return queryset.filter(date__lte=end_of_day) 