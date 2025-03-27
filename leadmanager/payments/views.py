from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
import datetime

from .models import Payment, PaymentMethod
from .forms import PaymentForm, PaymentFilterForm
from core.utils import can_access


@login_required
def payment_list(request):
    if not can_access(request.user, 'payments', 'view'):
        messages.error(request, "You don't have permission to view payments.")
        return redirect('dashboard:index')
    
    payments = Payment.objects.all()
    
    # Handle filtering
    filter_form = PaymentFilterForm(request.GET)
    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        payment_method = filter_form.cleaned_data.get('payment_method')
        
        if start_date:
            payments = payments.filter(payment_date__gte=start_date)
        
        if end_date:
            payments = payments.filter(payment_date__lte=end_date)
        
        if payment_method:
            payments = payments.filter(payment_method=payment_method)
    
    # Calculate total
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    # Handle search
    query = request.GET.get('q')
    if query:
        payments = payments.filter(
            Q(project__name__icontains=query) | 
            Q(receipt_number__icontains=query) |
            Q(notes__icontains=query)
        )
    
    context = {
        'payments': payments,
        'filter_form': filter_form,
        'total_payments': total_payments,
        'can_create': can_access(request.user, 'payments', 'create'),
    }
    return render(request, 'payments/payments_list.html', context)


@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    if not can_access(request.user, 'payments', 'view'):
        messages.error(request, "You don't have permission to view payment details.")
        return redirect('payments:payment_list')
    
    context = {
        'payment': payment,
        'can_update': can_access(request.user, 'payments', 'update'),
    }
    return render(request, 'payments/payment_detail.html', context)


@login_required
def payment_create(request):
    if not can_access(request.user, 'payments', 'create'):
        messages.error(request, "You don't have permission to create payments.")
        return redirect('payments:payment_list')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.save()
            messages.success(request, f"Payment of ${payment.amount} for '{payment.project.name}' created successfully.")
            return redirect('payments:payment_detail', pk=payment.pk)
    else:
        # Set default date to today
        form = PaymentForm(initial={'payment_date': datetime.date.today()})
    
    return render(request, 'payments/payment_form.html', {'form': form, 'title': 'Create Payment'})


@login_required
def payment_update(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    if not can_access(request.user, 'payments', 'update'):
        messages.error(request, "You don't have permission to update payments.")
        return redirect('payments:payment_detail', pk=payment.pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Payment updated successfully.")
            return redirect('payments:payment_detail', pk=payment.pk)
    else:
        form = PaymentForm(instance=payment)
    
    return render(request, 'payments/payment_form.html', {'form': form, 'payment': payment, 'title': 'Update Payment'})


@login_required
def payment_report(request):
    if not can_access(request.user, 'reports', 'view'):
        messages.error(request, "You don't have permission to view payment reports.")
        return redirect('dashboard:index')
    
    # All payments for reporting
    payments = Payment.objects.all()
    
    # Handle filtering
    filter_form = PaymentFilterForm(request.GET)
    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        payment_method = filter_form.cleaned_data.get('payment_method')
        
        if start_date:
            payments = payments.filter(payment_date__gte=start_date)
        
        if end_date:
            payments = payments.filter(payment_date__lte=end_date)
        
        if payment_method:
            payments = payments.filter(payment_method=payment_method)
    
    # Calculate totals for reporting
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    # Group by project for reporting
    projects = {}
    for payment in payments:
        project_id = payment.project.id
        if project_id not in projects:
            projects[project_id] = {
                'name': payment.project.name,
                'client': payment.project.client.name,
                'total': 0,
            }
        projects[project_id]['total'] += payment.amount
    
    # Convert to list for template
    projects_list = [projects[p_id] for p_id in projects]
    
    context = {
        'filter_form': filter_form,
        'payments': payments,
        'total_payments': total_payments,
        'projects': projects_list,
        'start_date': filter_form.cleaned_data.get('start_date'),
        'end_date': filter_form.cleaned_data.get('end_date'),
    }
    return render(request, 'reports/payment_report.html', context)
