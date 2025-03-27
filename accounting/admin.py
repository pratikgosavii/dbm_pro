from django.contrib import admin
from .models import Payment, Invoice, ExpenseCategory, Expense

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'project', 'payment_date', 'payment_method')
    list_filter = ('payment_date', 'payment_method')
    search_fields = ('project__name', 'notes')
    date_hierarchy = 'payment_date'

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'project', 'amount', 'issue_date', 'due_date', 'status')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('invoice_number', 'project__name')
    date_hierarchy = 'issue_date'

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'expense_date', 'category')
    list_filter = ('expense_date', 'category')
    search_fields = ('description',)
    date_hierarchy = 'expense_date'

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(ExpenseCategory)
admin.site.register(Expense, ExpenseAdmin)
