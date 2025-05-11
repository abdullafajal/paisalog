import django_filters
from django import forms
from .models import Entry

class EntryFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        label='From Date',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        label='To Date',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
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
        } 