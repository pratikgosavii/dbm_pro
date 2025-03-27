from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta, date
from leads.models import Lead
from projects.models import Project
from employees.models import Salary
from payments.models import Payment
import calendar

@login_required
def sales_report(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager):
        messages.error(request, "You don't have permission to view sales reports.")
        return redirect('dashboard:index')
    
    # Default to current month
    today = timezone.now().date()
    default_start = today.replace(day=1)
    default_end = today
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    rep_id = request.GET.get('sales_rep')
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = default_start
    else:
        start_date = default_start
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = default_end
    else:
        end_date = default_end
    
    # Query leads based on filters
    leads = Lead.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    if rep_id:
        leads = leads.filter(assigned_to_id=rep_id)
    
    # Aggregate data
    total_leads = leads.count()
    leads_by_source = leads.values('source__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    leads_by_status = leads.values('status__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    leads_by_rep = leads.values('assigned_to__username', 'assigned_to__first_name', 'assigned_to__last_name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Daily leads trend
    date_range = (end_date - start_date).days + 1
    daily_leads = []
    
    for i in range(date_range):
        day = start_date + timedelta(days=i)
        count = leads.filter(created_at__date=day).count()
        daily_leads.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    context = {
        'total_leads': total_leads,
        'leads_by_source': leads_by_source,
        'leads_by_status': leads_by_status,
        'leads_by_rep': leads_by_rep,
        'daily_leads': daily_leads,
        'start_date': start_date,
        'end_date': end_date,
        'current_rep': rep_id,
    }
    
    return render(request, 'reports/sales_report.html', context)

@login_required
def payment_report(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to view payment reports.")
        return redirect('dashboard:index')
    
    # Default to current month
    today = timezone.now().date()
    default_start = today.replace(day=1)
    default_end = today
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    project_id = request.GET.get('project')
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = default_start
    else:
        start_date = default_start
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = default_end
    else:
        end_date = default_end
    
    # Query payments based on filters
    payments = Payment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date
    )
    
    if project_id:
        payments = payments.filter(project_id=project_id)
    
    # Aggregate data
    total_payments = payments.count()
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    payments_by_status = payments.values('status').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')
    
    payments_by_method = payments.values('payment_method__name').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')
    
    # Calculate percentages for payment methods
    for method in payments_by_method:
        if total_amount > 0:
            method['percentage'] = (method['total'] / total_amount) * 100
        else:
            method['percentage'] = 0
    
    payments_by_project = payments.values('project__name').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')
    
    # Calculate percentages for projects
    for project in payments_by_project:
        if total_amount > 0:
            project['percentage'] = (project['total'] / total_amount) * 100
        else:
            project['percentage'] = 0
    
    # Daily payment trend
    date_range = (end_date - start_date).days + 1
    daily_payments = []
    
    for i in range(date_range):
        day = start_date + timedelta(days=i)
        day_payments = payments.filter(payment_date=day)
        amount = day_payments.aggregate(total=Sum('amount'))['total'] or 0
        daily_payments.append({
            'date': day.strftime('%Y-%m-%d'),
            'amount': amount
        })
    
    context = {
        'total_payments': total_payments,
        'total_amount': total_amount,
        'payments_by_status': payments_by_status,
        'payments_by_method': payments_by_method,
        'payments_by_project': payments_by_project,
        'daily_payments': daily_payments,
        'start_date': start_date,
        'end_date': end_date,
        'current_project': project_id,
    }
    
    return render(request, 'reports/payment_report.html', context)

@login_required
def salary_report(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to view salary reports.")
        return redirect('dashboard:index')
    
    # Default to current month/year
    today = timezone.now().date()
    default_month = today.month
    default_year = today.year
    
    # Get filter parameters
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month:
        try:
            month = int(month)
            if month < 1 or month > 12:
                month = default_month
        except ValueError:
            month = default_month
    else:
        month = default_month
    
    if year:
        try:
            year = int(year)
        except ValueError:
            year = default_year
    else:
        year = default_year
    
    # Query salaries based on filters
    salaries = Salary.objects.filter(month=month, year=year)
    
    # Aggregate data
    total_salaries = salaries.count()
    total_amount = salaries.aggregate(
        total=Sum('amount'),
        total_bonus=Sum('bonus'),
        total_deduction=Sum('deduction')
    )
    
    total_salary = total_amount['total'] or 0
    total_bonus = total_amount['total_bonus'] or 0
    total_deduction = total_amount['total_deduction'] or 0
    net_payout = total_salary + total_bonus - total_deduction
    
    salaries_by_status = salaries.values('status').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')
    
    # Generate month/year dropdown options
    month_choices = []
    for m in range(1, 13):
        month_name = calendar.month_name[m]
        month_choices.append((m, month_name))
    
    year_choices = []
    for y in range(year - 5, year + 1):
        year_choices.append(y)
    
    context = {
        'total_salaries': total_salaries,
        'total_salary': total_salary,
        'total_bonus': total_bonus,
        'total_deduction': total_deduction,
        'net_payout': net_payout,
        'salaries_by_status': salaries_by_status,
        'salaries': salaries,
        'current_month': month,
        'current_year': year,
        'month_choices': month_choices,
        'year_choices': year_choices,
    }
    
    return render(request, 'reports/salary_report.html', context)
