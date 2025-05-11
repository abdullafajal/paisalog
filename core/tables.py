import django_tables2 as tables
from .models import Entry, Category
from django.utils.safestring import mark_safe


class EntryTable(tables.Table):
    amount = tables.Column(verbose_name='Amount', empty_values=())
    date = tables.DateColumn(format="M d, Y")
    entry_type = tables.Column(verbose_name='Type', empty_values=())
    amount_type = tables.Column(verbose_name='Payment')
    actions = tables.TemplateColumn(
        template_name='entries/table_actions.html',
        verbose_name='',
        orderable=False
    )

    def render_amount(self, record):
        symbol = "₹"  # Default to Rupee symbol
        if record.amount_type == "online":
            symbol = "₹"  # Card symbol for online payments
        return f"{symbol}{record.amount}"

    def render_entry_type(self, record):
        entry_type = record.entry_type.capitalize()
        badge_class = "bg-success" if record.entry_type == "income" else "bg-danger"
        return mark_safe(f'<span class="badge {badge_class} text-white">{entry_type}</span>')


    def render_amount_type(self, record):
        amount_type = record.amount_type.capitalize()
        # badge_class = "text-success" if record.amount_type == "online" else "text-danger"
        badge_class = ""
        amount_type_icon = "💳" if record.amount_type == "online" else "💵"
        return mark_safe(f'<span class="{badge_class}">{amount_type_icon} {amount_type}</span>')

    class Meta:
        model = Entry
        template_name = "django_tables2/bootstrap4.html"
        fields = ('date', 'description', 'category', 'amount', 'entry_type', 'amount_type')
        attrs = {
            'class': 'table table-vcenter card-table',
            'thead': {
                'class': 'thead-light'
            }
        }


class RecentEntryTable(tables.Table):
    amount = tables.Column(verbose_name='Amount', empty_values=())
    date = tables.DateColumn(format="M d, Y")
    entry_type = tables.Column(verbose_name='Type', empty_values=())
    amount_type = tables.Column(verbose_name='Payment')

    def render_amount(self, record):
        symbol = "₹"  # Default to Rupee symbol
        if record.amount_type == "online":
            symbol = "₹"  # Card symbol for online payments
        return f"{symbol}{record.amount}"

    def render_entry_type(self, record):
        entry_type = record.entry_type.capitalize()
        badge_class = "bg-success" if record.entry_type == "income" else "bg-danger"
        return mark_safe(f'<span class="badge {badge_class} text-white">{entry_type}</span>')

    def render_amount_type(self, record):
        amount_type = record.amount_type.capitalize()
        amount_type_icon = "💳" if record.amount_type == "online" else "💵"
        return mark_safe(f'<span>{amount_type_icon} {amount_type}</span>')

    class Meta:
        model = Entry
        template_name = "django_tables2/bootstrap4.html"
        fields = ('date', 'category', 'description', 'amount', 'entry_type', 'amount_type')
        attrs = {
            'class': 'table table-vcenter card-table',
            'thead': {
                'class': 'thead-light'
            }
        }
        orderable = False

class CategoryTable(tables.Table):
    entry_type = tables.Column(verbose_name='Type', empty_values=())
    is_default = tables.Column(verbose_name='Status', empty_values=())
    created_at = tables.DateTimeColumn(format="M d, Y", verbose_name='Created')
    actions = tables.TemplateColumn(
        template_name='categories/table_actions.html',
        verbose_name='',
        orderable=False
    )

    def render_entry_type(self, record):
        entry_type = record.entry_type.capitalize()
        badge_class = "bg-success" if record.entry_type == "income" else "bg-danger"
        return mark_safe(f'<span class="badge {badge_class} text-white">{entry_type}</span>')

    def render_is_default(self, record):
        if record.is_default:
            return mark_safe('<span class="badge bg-secondary">System</span>')
        return mark_safe('<span class="badge bg-primary text-white">Custom</span>')

    class Meta:
        model = Category
        template_name = "django_tables2/bootstrap4.html"
        fields = ('name', 'entry_type', 'is_default', 'created_at', 'actions')
        attrs = {
            'class': 'table table-vcenter card-table',
            'thead': {
                'class': 'thead-light'
            }
        }
        order_by = ('name',)