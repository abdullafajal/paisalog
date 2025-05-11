from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, Entry
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        # Create a test user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='abdulla',
            email='abdulla@gmail.com'
        )
        if created:
            user.set_password('aa')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user'))

        # Sample categories
        categories = [
            'Salary',
            'Freelance',
            'Investments',
            'Food & Dining',
            'Transportation',
            'Shopping',
            'Bills & Utilities',
            'Entertainment',
            'Health & Fitness',
            'Travel',
        ]

        # Create categories
        for category_name in categories:
            Category.objects.get_or_create(
                name=category_name,
                user=user
            )
        self.stdout.write(self.style.SUCCESS('Created categories'))

        # Sample entries
        entry_types = ['income', 'expense']
        amount_types = ['cash', 'online']
        categories = Category.objects.filter(user=user)

        # Create entries for the last 6 months
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)

        current_date = start_date
        while current_date <= end_date:
            # Create 1-3 entries per day
            for _ in range(random.randint(1, 3)):
                entry_type = random.choice(entry_types)
                category = random.choice(categories)
                
                # Generate appropriate amount based on type and category
                if entry_type == 'income':
                    if category.name in ['Salary', 'Freelance']:
                        amount = random.randint(10000, 50000)
                    else:
                        amount = random.randint(1000, 5000)
                else:
                    if category.name in ['Food & Dining', 'Transportation']:
                        amount = random.randint(100, 500)
                    elif category.name in ['Shopping', 'Entertainment']:
                        amount = random.randint(500, 2000)
                    else:
                        amount = random.randint(200, 1000)

                Entry.objects.create(
                    user=user,
                    amount=amount,
                    category=category,
                    date=current_date,
                    description=f"Sample {entry_type} entry",
                    entry_type=entry_type,
                    amount_type=random.choice(amount_types)
                )

            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Created sample entries')) 