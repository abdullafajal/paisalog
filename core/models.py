from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    ENTRY_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES, default='expense')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Entry(models.Model):
    ENTRY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    AMOUNT_TYPES = [
        ('cash', 'Cash'),
        ('online', 'Online'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    amount_type = models.CharField(max_length=10, choices=AMOUNT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Entries"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.entry_type.title()} - {self.category.name} - ₹{self.amount}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_savings_target = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_salaried = models.BooleanField(default=False)
    salary_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salary_day = models.PositiveSmallIntegerField(default=1, help_text="Day of the month when salary is received")
    salary_frequency = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('biweekly', 'Bi-weekly'),
            ('weekly', 'Weekly')
        ],
        default='monthly'
    )
    salary_currency = models.CharField(max_length=3, default='INR')
    salary_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monthly deductions like tax, PF, etc.")
    salary_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monthly allowances like HRA, DA, etc.")

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_net_salary(self):
        """Calculate net salary after deductions and including allowances"""
        return self.salary_amount - self.salary_deductions + self.salary_allowances

    def get_daily_budget(self):
        """Calculate daily budget based on salary frequency"""
        if self.salary_frequency == 'monthly':
            return self.get_net_salary() / 30
        elif self.salary_frequency == 'biweekly':
            return self.get_net_salary() / 14
        else:  # weekly
            return self.get_net_salary() / 7

    def get_salary_date(self):
        """Get the next salary date"""
        today = timezone.now()
        if self.salary_frequency == 'monthly':
            if today.day >= self.salary_day:
                next_month = today.replace(day=1) + timedelta(days=32)
                return next_month.replace(day=self.salary_day)
            return today.replace(day=self.salary_day)
        elif self.salary_frequency == 'biweekly':
            days_until_salary = (self.salary_day - today.day) % 14
            return today + timedelta(days=days_until_salary)
        else:  # weekly
            days_until_salary = (self.salary_day - today.day) % 7
            return today + timedelta(days=days_until_salary)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile instance for new users"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile instance when the user is saved"""
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()
