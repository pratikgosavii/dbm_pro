from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Payment, PaymentMethod
from .forms import PaymentForm
from projects.models import Project

@login_required
def payment_list(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to view payments.")
        return redirect('dashboard:index')
    
    payments = Payment.objects.all()
    
    # Filter by project
    project_id = request.GET.get('project')
    if project_id:
        payments = payments.filter(project_id=project_id)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        payments = payments.filter(payment_date__gte=start_date)
    
    if end_date:
        payments = payments.filter(payment_date__lte=end_date)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        payments = payments.filter(status=status)
    
    # Filter by payment method
    method_id = request.GET.get('method')
    if method_id:
        payments = payments.filter(payment_method_id=method_id)
    
    # Order by most recent first
    payments = payments.order_by('-payment_date')
    
    # Calculate total amount
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get all projects and payment methods for filter dropdowns
    projects = Project.objects.all()
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    context = {
        'payments': payments,
        'projects': projects,
        'payment_methods': payment_methods,
        'current_project': project_id,
        'current_status': status,
        'current_method': method_id,
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': total_amount,
        'status_choices': Payment.STATUS_CHOICES,
    }
    
    return render(request, 'payments/payment_list.html', context)

@login_required
def payment_create(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to create payments.")
        return redirect('payments:payment_list')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.save()
            messages.success(request, 'Payment created successfully.')
            return redirect('payments:payment_list')
    else:
        # Pre-select the project if provided in URL
        project_id = request.GET.get('project')
        initial_data = {}
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                initial_data['project'] = project
            except Project.DoesNotExist:
                pass
        
        form = PaymentForm(initial=initial_data)
    
    context = {
        'form': form,
        'is_create': True,
    }
    
    return render(request, 'payments/payment_form.html', context)

@login_required
def payment_update(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to update payments.")
        return redirect('payments:payment_list')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment updated successfully.')
            return redirect('payments:payment_list')
    else:
        form = PaymentForm(instance=payment)
    
    context = {
        'form': form,
        'payment': payment,
        'is_create': False,
    }
    
    return render(request, 'payments/payment_form.html', context)
