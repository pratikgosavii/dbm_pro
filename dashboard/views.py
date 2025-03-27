from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from datetime import timedelta
from django.utils import timezone
from accounts.models import UserProfile
from leads.models import Lead
from projects.models import Project, Payment
from employees.models import Task, Attendance

@login_required
def index(request):
    """Main dashboard view with role-specific data"""
    user_profile = UserProfile.objects.get(user=request.user)
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    context = {
        'user_profile': user_profile,
    }
    
    # Admin metrics
    if user_profile.is_admin():
        # Lead metrics
        context['total_leads'] = Lead.objects.count()
        context['new_leads_today'] = Lead.objects.filter(created_at__date=today).count()
        context['lead_status_counts'] = Lead.objects.values('status').annotate(count=Count('id'))
        
        # Project metrics
        context['active_projects'] = Project.objects.filter(status__in=['new', 'in_progress']).count()
        context['completed_projects'] = Project.objects.filter(status='completed').count()
        
        # Payment metrics
        context['total_payments'] = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['payments_this_month'] = Payment.objects.filter(
            payment_date__gte=this_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['payments_last_month'] = Payment.objects.filter(
            payment_date__gte=last_month_start,
            payment_date__lt=this_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Task metrics
        context['overdue_tasks'] = Task.objects.filter(
            due_date__lt=today,
            status__in=['todo', 'in_progress', 'review']
        ).count()
        context['tasks_completed_today'] = Task.objects.filter(
            status='done',
            updated_at__date=today
        ).count()
        
        # Attendance metrics
        context['employees_present_today'] = Attendance.objects.filter(date=today).count()
    
    # Manager metrics
    elif user_profile.is_manager():
        # Lead metrics
        context['total_leads'] = Lead.objects.count()
        context['unassigned_leads'] = Lead.objects.filter(assigned_to__isnull=True).count()
        context['lead_status_counts'] = Lead.objects.values('status').annotate(count=Count('id'))
        
        # Task metrics
        context['overdue_tasks'] = Task.objects.filter(
            due_date__lt=today,
            status__in=['todo', 'in_progress', 'review']
        ).count()
        context['tasks_completed_today'] = Task.objects.filter(
            status='done',
            updated_at__date=today
        ).count()
        
        # Attendance metrics
        context['employees_present_today'] = Attendance.objects.filter(date=today).count()
    
    # Operations Manager metrics
    elif user_profile.is_operations_manager():
        # Project metrics
        context['active_projects'] = Project.objects.filter(status__in=['new', 'in_progress']).count()
        context['completed_projects'] = Project.objects.filter(status='completed').count()
        
        # Payment metrics
        context['total_payments'] = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['payments_this_month'] = Payment.objects.filter(
            payment_date__gte=this_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Task metrics
        context['overdue_tasks'] = Task.objects.filter(
            due_date__lt=today,
            status__in=['todo', 'in_progress', 'review']
        ).count()
    
    # Sales Rep metrics
    elif user_profile.is_sales_rep():
        # My lead metrics
        context['my_total_leads'] = Lead.objects.filter(assigned_to=request.user).count()
        context['my_new_leads'] = Lead.objects.filter(
            assigned_to=request.user,
            status='new'
        ).count()
        context['my_lead_status_counts'] = Lead.objects.filter(
            assigned_to=request.user
        ).values('status').annotate(count=Count('id'))
        
        # My task metrics
        context['my_tasks'] = Task.objects.filter(assigned_to=request.user).count()
        context['my_overdue_tasks'] = Task.objects.filter(
            assigned_to=request.user,
            due_date__lt=today,
            status__in=['todo', 'in_progress', 'review']
        ).count()
    
    # Developer metrics
    elif user_profile.is_developer():
        # My project metrics
        context['my_projects'] = Project.objects.filter(assigned_developers=request.user).count()
        context['my_active_projects'] = Project.objects.filter(
            assigned_developers=request.user,
            status__in=['new', 'in_progress']
        ).count()
        
        # My task metrics
        context['my_tasks'] = Task.objects.filter(assigned_to=request.user).count()
        context['my_todo_tasks'] = Task.objects.filter(
            assigned_to=request.user,
            status='todo'
        ).count()
        context['my_in_progress_tasks'] = Task.objects.filter(
            assigned_to=request.user,
            status='in_progress'
        ).count()
        context['my_review_tasks'] = Task.objects.filter(
            assigned_to=request.user,
            status='review'
        ).count()
        context['my_overdue_tasks'] = Task.objects.filter(
            assigned_to=request.user,
            due_date__lt=today,
            status__in=['todo', 'in_progress', 'review']
        ).count()
    
    # Get today's attendance for check-in button
    try:
        context['today_attendance'] = Attendance.objects.get(
            employee=request.user,
            date=today
        )
    except Attendance.DoesNotExist:
        context['today_attendance'] = None
    
    return render(request, 'dashboard/index.html', context)
