from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from leads.models import Lead, LeadStatus
from projects.models import Project, ProjectStatus
from employees.models import Attendance, Salary
from payments.models import Payment

@login_required
def index(request):
    # Get the user's profile
    user_profile = request.user.userprofile
    role = user_profile.role
    
    # Get date range for dashboard stats
    today = timezone.now().date()
    month_start = today.replace(day=1)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)
    
    # Role-specific dashboard data
    context = {
        'user_profile': user_profile,
    }
    
    # Admin Dashboard
    if role == 'admin':
        # Lead stats
        total_leads = Lead.objects.count()
        new_leads_month = Lead.objects.filter(created_at__gte=month_start).count()
        
        # Lead by status
        lead_statuses = LeadStatus.objects.filter(is_active=True)
        leads_by_status = []
        for status in lead_statuses:
            count = Lead.objects.filter(status=status).count()
            leads_by_status.append({
                'status': status.name,
                'count': count,
            })
        
        # Project stats
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(
            Q(end_date__isnull=True) | Q(end_date__gt=today)
        ).count()
        
        # Project by status
        project_statuses = ProjectStatus.objects.filter(is_active=True)
        projects_by_status = []
        for status in project_statuses:
            count = Project.objects.filter(status=status).count()
            projects_by_status.append({
                'status': status.name,
                'count': count,
            })
        
        # Payment stats
        total_payments = Payment.objects.filter(
            payment_date__gte=month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        last_month_payments = Payment.objects.filter(
            payment_date__gte=last_month_start,
            payment_date__lt=month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Employee stats
        total_employees = Attendance.objects.filter(
            date=today
        ).count()
        
        context.update({
            'total_leads': total_leads,
            'new_leads_month': new_leads_month,
            'leads_by_status': leads_by_status,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'projects_by_status': projects_by_status,
            'total_payments': total_payments,
            'last_month_payments': last_month_payments,
            'total_employees': total_employees,
        })
    
    # Manager Dashboard
    elif role == 'manager':
        # Lead stats
        total_leads = Lead.objects.count()
        new_leads_month = Lead.objects.filter(created_at__gte=month_start).count()
        
        # Unassigned leads
        unassigned_leads = Lead.objects.filter(assigned_to__isnull=True).count()
        
        # Lead by status
        lead_statuses = LeadStatus.objects.filter(is_active=True)
        leads_by_status = []
        for status in lead_statuses:
            count = Lead.objects.filter(status=status).count()
            leads_by_status.append({
                'status': status.name,
                'count': count,
            })
            
        context.update({
            'total_leads': total_leads,
            'new_leads_month': new_leads_month,
            'unassigned_leads': unassigned_leads,
            'leads_by_status': leads_by_status,
        })
    
    # Sales Rep Dashboard
    elif role == 'sales_rep':
        # Lead stats for this sales rep
        assigned_leads = Lead.objects.filter(assigned_to=request.user).count()
        new_leads_month = Lead.objects.filter(
            assigned_to=request.user,
            created_at__gte=month_start
        ).count()
        
        # Lead by status
        lead_statuses = LeadStatus.objects.filter(is_active=True)
        leads_by_status = []
        for status in lead_statuses:
            count = Lead.objects.filter(
                assigned_to=request.user,
                status=status
            ).count()
            leads_by_status.append({
                'status': status.name,
                'count': count,
            })
            
        context.update({
            'assigned_leads': assigned_leads,
            'new_leads_month': new_leads_month,
            'leads_by_status': leads_by_status,
        })
    
    # Operations Manager Dashboard
    elif role == 'ops_manager':
        # Project stats
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(
            Q(end_date__isnull=True) | Q(end_date__gt=today)
        ).count()
        
        # Project by status
        project_statuses = ProjectStatus.objects.filter(is_active=True)
        projects_by_status = []
        for status in project_statuses:
            count = Project.objects.filter(status=status).count()
            projects_by_status.append({
                'status': status.name,
                'count': count,
            })
        
        # Payment stats
        total_payments = Payment.objects.filter(
            payment_date__gte=month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Employee attendance today
        employees_present = Attendance.objects.filter(
            date=today,
            status='present'
        ).count()
        
        context.update({
            'total_projects': total_projects,
            'active_projects': active_projects,
            'projects_by_status': projects_by_status,
            'total_payments': total_payments,
            'employees_present': employees_present,
        })
    
    # Developer Dashboard
    elif role == 'developer':
        # Project stats for this developer
        assigned_projects = request.user.assigned_projects.count()
        active_projects = request.user.assigned_projects.filter(
            Q(end_date__isnull=True) | Q(end_date__gt=today)
        ).count()
        
        # Project by status
        project_statuses = ProjectStatus.objects.filter(is_active=True)
        projects_by_status = []
        for status in project_statuses:
            count = request.user.assigned_projects.filter(status=status).count()
            projects_by_status.append({
                'status': status.name,
                'count': count,
            })
        
        # Get current attendance status
        try:
            today_attendance = Attendance.objects.get(
                employee=request.user,
                date=today
            )
            is_punched_in = bool(today_attendance.punch_in_time)
            is_punched_out = bool(today_attendance.punch_out_time)
        except Attendance.DoesNotExist:
            is_punched_in = False
            is_punched_out = False
        
        context.update({
            'assigned_projects': assigned_projects,
            'active_projects': active_projects,
            'projects_by_status': projects_by_status,
            'is_punched_in': is_punched_in,
            'is_punched_out': is_punched_out,
        })
    
    return render(request, 'dashboard/index.html', context)
