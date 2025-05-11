from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import template
from .models import Entry, Category, UserProfile
from django.db import models

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['entry_type', 'amount', 'category', 'date', 'description', 'amount_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amount_type': forms.Select(attrs={'class': 'form-control'}),
            'entry_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Get entry type from URL parameter for new entries
        if not self.instance.pk and self.request:
            entry_type = self.request.GET.get('type', 'expense')
            self.initial['entry_type'] = entry_type
            
            # Filter categories based on entry type
            self.fields['category'].queryset = Category.objects.filter(
                models.Q(user=self.request.user) | models.Q(is_default=True),
                entry_type=entry_type
            )
        elif self.instance.pk:
            # For existing entries, filter categories based on the entry's type
            self.fields['category'].queryset = Category.objects.filter(
                models.Q(user=self.request.user) | models.Q(is_default=True),
                entry_type=self.instance.entry_type
            )

    def clean(self):
        cleaned_data = super().clean()
        entry_type = cleaned_data.get('entry_type')
        category = cleaned_data.get('category')

        if entry_type and category:
            if category.entry_type != entry_type:
                raise forms.ValidationError(
                    "Selected category does not match the entry type."
                )

        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'entry_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'entry_type': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['name'].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'monthly_budget', 'monthly_savings_target',
            'is_salaried', 'salary_amount', 'salary_day',
            'salary_frequency', 'salary_currency',
            'salary_deductions', 'salary_allowances'
        ]
        widgets = {
            'monthly_budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_savings_target': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_salaried': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'salary_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_day': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 31}),
            'salary_frequency': forms.Select(attrs={'class': 'form-select'}),
            'salary_currency': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 3}),
            'salary_deductions': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_allowances': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text for salary fields
        self.fields['salary_amount'].help_text = 'Your gross salary amount'
        self.fields['salary_day'].help_text = 'Day of the month when you receive your salary'
        self.fields['salary_deductions'].help_text = 'Monthly deductions like tax, PF, etc.'
        self.fields['salary_allowances'].help_text = 'Monthly allowances like HRA, DA, etc.'

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={**field.field.widget.attrs, 'class': css}) 