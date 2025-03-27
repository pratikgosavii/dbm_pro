from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
import datetime

from leads.models import Lead, LeadStatus
from projects.models import Project, Task
from payments.models import Payment
from employees.models import Employee, TimeRecord


@login_required
def index(request):
    """
    Dashboard view showing role-specific data
    """
    context = {}
    user_role = request.user.profile.role
    
    # Admin dashboard
    if user_role == 'admin':
        # Lead metrics
        total_leads = Lead.objects.count()
        new_leads = Lead.objects.filter(status__name='New').count()
        converted_leads = Lead.objects.filter(status__name='Converted').count()
        
        # Project metrics
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status__name='In Progress').count()
        
        # Payment metrics
        total_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        # Recent activities
        recent_leads = Lead.objects.all()[:5]
        recent_projects = Project.objects.all()[:5]
        recent_payments = Payment.objects.all()[:5]
        
        context.update({
            'total_leads': total_leads,
            'new_leads': new_leads,
            'converted_leads': converted_leads,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_payments': total_payments,
            'recent_leads': recent_leads,
            'recent_projects': recent_projects,
            'recent_payments': recent_payments,
        })
    
    # Manager dashboard
    elif user_role == 'manager':
        # Lead metrics
        total_leads = Lead.objects.count()
        unassigned_leads = Lead.objects.filter(assigned_to__isnull=True).count()
        
        # Sales rep performance
        sales_reps = Lead.objects.values('assigned_to__username', 'assigned_to__first_name', 'assigned_to__last_name').annotate(
            total_leads=Count('id')
        ).filter(assigned_to__isnull=False).order_by('-total_leads')[:5]
        
        # Recent leads
        recent_leads = Lead.objects.all()[:10]
        
        context.update({
            'total_leads': total_leads,
            'unassigned_leads': unassigned_leads,
            'sales_reps': sales_reps,
            'recent_leads': recent_leads,
        })
    
    # Sales Rep dashboard
    elif user_role == 'sales_rep':
        # My leads
        my_leads = Lead.objects.filter(assigned_to=request.user)
        total_my_leads = my_leads.count()
        
        # Status breakdown
        lead_statuses = LeadStatus.objects.all()
        status_counts = []
        for status in lead_statuses:
            count = my_leads.filter(status=status).count()
            status_counts.append({
                'name': status.name,
                'count': count
            })
        
        # Recent leads
        recent_leads = my_leads[:10]
        
        context.update({
            'total_my_leads': total_my_leads,
            'status_counts': status_counts,
            'recent_leads': recent_leads,
        })
    
    # Operations Manager dashboard
    elif user_role == 'operations_manager':
        # Project metrics
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status__name='In Progress').count()
        
        # Payment metrics
        total_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        # Recent activities
        recent_projects = Project.objects.all()[:5]
        recent_payments = Payment.objects.all()[:5]
        
        context.update({
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_payments': total_payments,
            'recent_projects': recent_projects,
            'recent_payments': recent_payments,
        })
    
    # Developer dashboard
    elif user_role == 'developer':
        # My tasks
        my_tasks = Task.objects.filter(assigned_to=request.user)
        total_my_tasks = my_tasks.count()
        
        # Task status breakdown
        task_statuses = {
            'pending': my_tasks.filter(status='pending').count(),
            'in_progress': my_tasks.filter(status='in_progress').count(),
            'completed': my_tasks.filter(status='completed').count(),
            'on_hold': my_tasks.filter(status='on_hold').count(),
        }
        
        # Recent tasks
        recent_tasks = my_tasks[:10]
        
        # Projects I'm working on
        my_projects = Project.objects.filter(tasks__assigned_to=request.user).distinct()
        
        # Time tracking for today
        try:
            employee = request.user.employee
            today = datetime.date.today()
            today_record = TimeRecord.objects.filter(employee=employee, date=today).first()
        except:
            employee = None
            today_record = None
        
        context.update({
            'total_my_tasks': total_my_tasks,
            'task_statuses': task_statuses,
            'recent_tasks': recent_tasks,
            'my_projects': my_projects,
            'employee': employee,
            'today_record': today_record,
        })
    
    # Add user role to context
    context['user_role'] = user_role
    
    return render(request, 'dashboard/index.html', context)
