from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import SingleTableView, RequestConfig
from django_tables2.export import ExportMixin
from django_filters.views import FilterView
from collections import defaultdict
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from datetime import timedelta, datetime
import json
from django_tables2.export.export import TableExport
from django_tables2 import SingleTableMixin
from django.views.decorators.cache import cache_control
from django.conf import settings
import os
from django.core.paginator import Paginator
from django_tables2.paginators import LazyPaginator

from .forms import SignUpForm, EntryForm, CategoryForm, UserProfileForm
from .models import Entry, Category, UserProfile
from .tables import EntryTable, CategoryTable, RecentEntryTable
from .filters import EntryFilter

def create_default_categories():
    default_categories = [
        # Income categories
        {'name': 'Salary', 'entry_type': 'income'},
        {'name': 'Freelance', 'entry_type': 'income'},
        {'name': 'Investments', 'entry_type': 'income'},
        {'name': 'Gifts', 'entry_type': 'income'},
        {'name': 'Other Income', 'entry_type': 'income'},
        
        # Expense categories
        {'name': 'Food & Dining', 'entry_type': 'expense'},
        {'name': 'Transportation', 'entry_type': 'expense'},
        {'name': 'Housing', 'entry_type': 'expense'},
        {'name': 'Utilities', 'entry_type': 'expense'},
        {'name': 'Entertainment', 'entry_type': 'expense'},
        {'name': 'Shopping', 'entry_type': 'expense'},
        {'name': 'Healthcare', 'entry_type': 'expense'},
        {'name': 'Education', 'entry_type': 'expense'},
        {'name': 'Travel', 'entry_type': 'expense'},
        {'name': 'Other Expenses', 'entry_type': 'expense'},
    ]
    
    for category_data in default_categories:
        Category.objects.get_or_create(
            name=category_data['name'],
            entry_type=category_data['entry_type'],
            is_default=True
        )

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile for the new user
            UserProfile.objects.create(user=user)
            login(request, user)
            # Create default categories for new user
            create_default_categories()
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})

def logout_view(request):
    auth_logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    # Get date range
    period_type = request.GET.get('period_type', 'month')
    end_date = timezone.now().date()
    
    if period_type == 'year':
        start_date = end_date - timedelta(days=365)
    elif period_type == 'month':
        start_date = end_date - timedelta(days=30)
    else:  # day
        start_date = end_date - timedelta(days=1)

    # Convert date range to timezone-aware datetime objects
    start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

    # Get user's entries with proper timezone handling
    user_entries = Entry.objects.filter(
        user=request.user,
        date__range=[start_datetime, end_datetime]
    )

    # Calculate totals
    total_income = user_entries.filter(entry_type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = user_entries.filter(entry_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    current_balance = total_income - total_expenses

    # Calculate savings rate
    if total_income > 0:
        savings_rate = ((total_income - total_expenses) / total_income) * 100
    else:
        savings_rate = 0

    # Calculate budget utilization
    if hasattr(request.user, 'profile') and request.user.profile.salary_amount:
        budget_utilization = (total_expenses / request.user.profile.salary_amount) * 100
    else:
        budget_utilization = 0

    # Get recent transactions
    recent_transactions = Entry.objects.filter(user=request.user).order_by('-date', '-created_at')[:5]
    recent_table = RecentEntryTable(recent_transactions)
    RequestConfig(request).configure(recent_table)

    # Get top categories
    top_categories = []
    for category in Category.objects.filter(
        Q(user=request.user) | Q(is_default=True)
    ).distinct():
        category_total = user_entries.filter(category=category).aggregate(total=Sum('amount'))['total'] or 0
        if category_total > 0:
            percentage = (category_total / (total_income + total_expenses)) * 100 if (total_income + total_expenses) > 0 else 0
            top_categories.append({
                'name': category.name,
                'total': category_total,
                'type': category.entry_type,
                'percentage': percentage
            })

    # Sort categories by total amount
    top_categories.sort(key=lambda x: x['total'], reverse=True)
    top_categories = top_categories[:4]  # Get top 4 categories

    # Prepare chart data
    monthly_data = []
    savings_trend = []
    category_data = []

    # Monthly data for income vs expenses
    current_date = start_date
    while current_date <= end_date:
        # Calculate first and last day of the month
        month_start = current_date.replace(day=1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        month_end = next_month - timedelta(days=1)
        
        # Use date range filtering instead of date__month and date__year
        month_entries = user_entries.filter(
            date__gte=timezone.make_aware(datetime.combine(month_start, datetime.min.time())),
            date__lte=timezone.make_aware(datetime.combine(month_end, datetime.max.time()))
        )
        
        month_income = month_entries.filter(entry_type='income').aggregate(total=Sum('amount'))['total'] or 0
        month_expenses = month_entries.filter(entry_type='expense').aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': current_date.strftime('%b %Y'),
            'income': float(month_income),
            'expenses': float(month_expenses)
        })
        
        # Calculate savings trend
        target_savings = float(total_income) * 0.2  # 20% of total income as target
        actual_savings = float(month_income - month_expenses)
        savings_trend.append({
            'month': current_date.strftime('%b %Y'),
            'savings': actual_savings,
            'target': target_savings
        })
        
        # Move to the next month
        current_date = next_month

    # Category distribution data
    for category in Category.objects.filter(
        Q(user=request.user) | Q(is_default=True)
    ).distinct():
        category_total = user_entries.filter(category=category).aggregate(total=Sum('amount'))['total'] or 0
        if category_total > 0:
            category_data.append({
                'name': category.name,
                'expenses': float(category_total) if category.entry_type == 'expense' else 0,
                'income': float(category_total) if category.entry_type == 'income' else 0
            })

    # Payment Method Distribution data
    payment_method_data = []
    cash_total = user_entries.filter(amount_type='cash', entry_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    online_total = user_entries.filter(amount_type='online', entry_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    
    if cash_total > 0:
        payment_method_data.append({
            'method': 'Cash',
            'amount': float(cash_total)
        })
    
    if online_total > 0:
        payment_method_data.append({
            'method': 'Online',
            'amount': float(online_total)
        })
    
    # Spending Metrics
    avg_daily_expense = 0
    if period_type == 'year':
        avg_daily_expense = total_expenses / 365 if total_expenses > 0 else 0
    elif period_type == 'month':
        avg_daily_expense = total_expenses / 30 if total_expenses > 0 else 0
    else:  # day
        avg_daily_expense = total_expenses

    expenses_by_day = {}
    for entry in user_entries.filter(entry_type='expense'):
        # Use the date field converted to timezone-aware date for day of week
        day_of_week = timezone.localtime(entry.date).strftime('%A')
        if day_of_week not in expenses_by_day:
            expenses_by_day[day_of_week] = 0
        expenses_by_day[day_of_week] += float(entry.amount)
    
    highest_spending_day = max(expenses_by_day.items(), key=lambda x: x[1]) if expenses_by_day else ('N/A', 0)
    
    # Transaction Count
    income_count = user_entries.filter(entry_type='income').count()
    expense_count = user_entries.filter(entry_type='expense').count()
    total_count = income_count + expense_count
    
    # Get transaction counts by day for the chart
    transaction_count_data = []
    current_date = start_date
    while current_date <= end_date:
        # Create timezone-aware datetime objects for the start and end of the day
        day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
        day_end = timezone.make_aware(datetime.combine(current_date, datetime.max.time()))
        
        # Filter entries for the current day
        day_entries = user_entries.filter(date__gte=day_start, date__lte=day_end)
        day_income_count = day_entries.filter(entry_type='income').count()
        day_expense_count = day_entries.filter(entry_type='expense').count()
        
        transaction_count_data.append({
            'date': current_date.strftime('%d %b'),
            'income': day_income_count,
            'expense': day_expense_count,
            'total': day_income_count + day_expense_count
        })
        
        current_date += timedelta(days=1)

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'current_balance': current_balance,
        'savings_rate': savings_rate,
        'savings_progress': min(savings_rate / 20 * 100, 100),  # Progress towards 20% savings goal
        'budget_utilization': budget_utilization,
        'top_categories': top_categories,
        'monthly_data': json.dumps(monthly_data),
        'category_data': json.dumps(category_data),
        'savings_trend': json.dumps(savings_trend),
        'period_type': period_type,
        'start_date': start_date,
        'end_date': end_date,
        'recent_table': recent_table,
        'payment_method_data': json.dumps(payment_method_data),
        'avg_daily_expense': avg_daily_expense,
        'highest_spending_day': highest_spending_day,
        'income_count': income_count,
        'expense_count': expense_count,
        'total_count': total_count,
        'transaction_count_data': json.dumps(transaction_count_data),
    }

    return render(request, 'dashboard.html', context)

class EntryListView(LoginRequiredMixin, ExportMixin, FilterView, SingleTableView):
    model = Entry
    table_class = EntryTable
    filterset_class = EntryFilter
    template_name = 'entries/list.html'
    paginate_by = 10
    export_formats = ['csv', 'xlsx']
    paginator_class = LazyPaginator

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_entries = Entry.objects.filter(user=self.request.user)
        
        # Calculate totals
        total_income = user_entries.filter(entry_type='income').aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = user_entries.filter(entry_type='expense').aggregate(total=Sum('amount'))['total'] or 0
        current_balance = total_income - total_expenses

        context.update({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'current_balance': current_balance,
        })
        return context

class EntryCreateView(LoginRequiredMixin, CreateView):
    model = Entry
    form_class = EntryForm
    template_name = 'entries/form.html'
    success_url = reverse_lazy('entry_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EntryUpdateView(LoginRequiredMixin, UpdateView):
    model = Entry
    form_class = EntryForm
    template_name = 'entries/form.html'
    success_url = reverse_lazy('entry_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)

class EntryDeleteView(LoginRequiredMixin, DeleteView):
    model = Entry
    success_url = '/entries/'
    template_name = 'entries/confirm_delete.html'

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)

class CategoryListView(LoginRequiredMixin, SingleTableView):
    model = Category
    table_class = CategoryTable
    template_name = 'categories/list.html'
    context_object_name = 'object_list'
    paginate_by = 10
    paginator_class = LazyPaginator

    def get_queryset(self):
        return Category.objects.filter(
            Q(user=self.request.user) | Q(is_default=True)
        ).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.get_table(**self.get_table_kwargs())
        context['table'] = table
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/form.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'categories/confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'profile_form.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        # Ensure the profile exists
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def service_worker(request):
    response = HttpResponse(
        open(os.path.join(settings.STATICFILES_DIRS[0], 'sw.js')).read(),
        content_type='application/javascript'
    )
    return response
