from django.contrib import admin
from .models import Payment, PaymentMethod

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('project', 'amount', 'payment_date', 'payment_method', 'status')
    list_filter = ('payment_date', 'payment_method', 'status')
    search_fields = ('project__name', 'notes')
    date_hierarchy = 'payment_date'

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
