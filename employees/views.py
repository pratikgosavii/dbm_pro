from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Attendance, Salary, EmployeeTask
from .forms import AttendanceForm, SalaryForm, PunchForm, EmployeeTaskForm

@login_required
def employee_list(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to view employees.")
        return redirect('dashboard:index')
    
    # Get employees with search filter
    employees = User.objects.all()
    query = request.GET.get('q')
    if query:
        employees = employees.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(email__icontains=query)
        )
    
    # Filter by role
    role = request.GET.get('role')
    if role:
        employees = employees.filter(userprofile__role=role)
    
    context = {
        'employees': employees,
        'query': query,
        'current_role': role,
    }
    
    return render(request, 'employees/employee_list.html', context)

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(User, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager or request.user.pk == pk):
        messages.error(request, "You don't have permission to view this employee.")
        return redirect('employees:employee_list')
    
    # Get attendance records
    attendances = Attendance.objects.filter(employee=employee).order_by('-date')[:30]
    
    # Get salary records
    salaries = Salary.objects.filter(employee=employee).order_by('-year', '-month')[:12]
    
    # Get task records
    tasks = EmployeeTask.objects.filter(assigned_to=employee).order_by('-created_at')[:10]
    
    context = {
        'employee': employee,
        'attendances': attendances,
        'salaries': salaries,
        'tasks': tasks,
    }
    
    return render(request, 'employees/employee_detail.html', context)

@login_required
def attendance_log(request):
    # Show all attendance for admins/managers, but only own attendance for others
    user_profile = request.user.userprofile
    
    # Initialize employee_id variable
    employee_id = None
    
    if user_profile.is_admin or user_profile.is_ops_manager:
        attendances = Attendance.objects.all()
        
        # Filter by employee
        employee_id = request.GET.get('employee')
        if employee_id:
            attendances = attendances.filter(employee_id=employee_id)
    else:
        attendances = Attendance.objects.filter(employee=request.user)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        attendances = attendances.filter(date__gte=start_date)
    
    if end_date:
        attendances = attendances.filter(date__lte=end_date)
    
    # Order by most recent first
    attendances = attendances.order_by('-date')
    
    # Get all employees for the filter dropdown (for admins/managers)
    employees = None
    if user_profile.is_admin or user_profile.is_ops_manager:
        employees = User.objects.all()
    
    context = {
        'attendances': attendances,
        'employees': employees,
        'current_employee': employee_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'employees/punch_log.html', context)

@login_required
def punch_in(request):
    today = timezone.now().date()
    
    # Check if already punched in today
    attendance, created = Attendance.objects.get_or_create(
        employee=request.user,
        date=today,
        defaults={
            'punch_in_time': timezone.now().time(),
            'status': 'present'
        }
    )
    
    if not created:
        if attendance.punch_in_time:
            messages.info(request, "You have already punched in today.")
        else:
            attendance.punch_in_time = timezone.now().time()
            attendance.save()
            messages.success(request, "Punch-in recorded successfully.")
    else:
        messages.success(request, "Punch-in recorded successfully.")
    
    return redirect('dashboard:index')

@login_required
def punch_out(request):
    today = timezone.now().date()
    
    try:
        attendance = Attendance.objects.get(employee=request.user, date=today)
        
        if not attendance.punch_in_time:
            messages.error(request, "You need to punch in first.")
        elif attendance.punch_out_time:
            messages.info(request, "You have already punched out today.")
        else:
            attendance.punch_out_time = timezone.now().time()
            attendance.save()
            messages.success(request, "Punch-out recorded successfully.")
    except Attendance.DoesNotExist:
        messages.error(request, "You need to punch in first.")
    
    return redirect('dashboard:index')

@login_required
def salary_list(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to view salaries.")
        return redirect('dashboard:index')
    
    salaries = Salary.objects.all()
    
    # Filter by employee
    employee_id = request.GET.get('employee')
    if employee_id:
        salaries = salaries.filter(employee_id=employee_id)
    
    # Filter by month and year
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month:
        salaries = salaries.filter(month=month)
    
    if year:
        salaries = salaries.filter(year=year)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        salaries = salaries.filter(status=status)
    
    # Order by most recent first
    salaries = salaries.order_by('-year', '-month')
    
    # Get all employees for the filter dropdown
    employees = User.objects.all()
    
    context = {
        'salaries': salaries,
        'employees': employees,
        'current_employee': employee_id,
        'current_month': month,
        'current_year': year,
        'current_status': status,
        'month_choices': Salary.MONTH_CHOICES,
        'status_choices': Salary.STATUS_CHOICES,
    }
    
    return render(request, 'employees/salary_list.html', context)

@login_required
def salary_create(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to create salaries.")
        return redirect('employees:salary_list')
    
    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            salary = form.save(commit=False)
            salary.created_by = request.user
            
            # Check if salary for this month/year already exists
            existing = Salary.objects.filter(
                employee=salary.employee,
                month=salary.month,
                year=salary.year
            ).exists()
            
            if existing:
                messages.error(request, f"Salary for {salary.get_month_display()} {salary.year} already exists for this employee.")
            else:
                salary.save()
                messages.success(request, 'Salary created successfully.')
                return redirect('employees:salary_list')
    else:
        form = SalaryForm()
    
    context = {
        'form': form,
        'is_create': True,
    }
    
    return render(request, 'employees/salary_form.html', context)

@login_required
def salary_update(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to update salaries.")
        return redirect('employees:salary_list')
    
    if request.method == 'POST':
        form = SalaryForm(request.POST, instance=salary)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary updated successfully.')
            return redirect('employees:salary_list')
    else:
        form = SalaryForm(instance=salary)
    
    context = {
        'form': form,
        'salary': salary,
        'is_create': False,
    }
    
    return render(request, 'employees/salary_form.html', context)

# Task Management Views
@login_required
def task_list(request):
    user_profile = request.user.userprofile
    
    # Determine which tasks to show based on user role
    if user_profile.is_admin or user_profile.is_manager:
        # Admins and managers can see all tasks
        tasks = EmployeeTask.objects.all()
        
        # Filter by assigned employee if specified
        employee_id = request.GET.get('employee')
        if employee_id:
            tasks = tasks.filter(assigned_to_id=employee_id)
    else:
        # Regular users can only see their own tasks
        tasks = EmployeeTask.objects.filter(assigned_to=request.user)
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)
    
    # Filter by priority if specified
    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)
    
    # Get all employees for filter dropdown (if user is admin/manager)
    employees = None
    if user_profile.is_admin or user_profile.is_manager:
        employees = User.objects.all()
    
    context = {
        'tasks': tasks,
        'employees': employees,
        'current_employee': request.GET.get('employee'),
        'current_status': status,
        'current_priority': priority,
        'status_choices': EmployeeTask.STATUS_CHOICES,
        'priority_choices': EmployeeTask.PRIORITY_CHOICES
    }
    
    return render(request, 'employees/task_list.html', context)

@login_required
def task_detail(request, pk):
    task = get_object_or_404(EmployeeTask, pk=pk)
    
    # Check permissions
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager or task.assigned_to == request.user or task.assigned_by == request.user):
        messages.error(request, "You don't have permission to view this task.")
        return redirect('employees:task_list')
    
    context = {
        'task': task
    }
    
    return render(request, 'employees/task_detail.html', context)

@login_required
def task_create(request):
    user_profile = request.user.userprofile
    
    if request.method == 'POST':
        form = EmployeeTaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            messages.success(request, 'Task created successfully.')
            return redirect('employees:task_list')
    else:
        form = EmployeeTaskForm(user=request.user)
    
    context = {
        'form': form,
        'is_create': True
    }
    
    return render(request, 'employees/task_form.html', context)

@login_required
def task_update(request, pk):
    task = get_object_or_404(EmployeeTask, pk=pk)
    
    # Check permissions
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager or task.assigned_by == request.user):
        messages.error(request, "You don't have permission to update this task.")
        return redirect('employees:task_list')
    
    if request.method == 'POST':
        form = EmployeeTaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('employees:task_detail', pk=task.pk)
    else:
        form = EmployeeTaskForm(instance=task, user=request.user)
    
    context = {
        'form': form,
        'task': task,
        'is_create': False
    }
    
    return render(request, 'employees/task_form.html', context)

@login_required
def task_complete(request, pk):
    task = get_object_or_404(EmployeeTask, pk=pk)
    
    # Check permissions (only assigned employee or admin/manager can mark as complete)
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager or task.assigned_to == request.user):
        messages.error(request, "You don't have permission to complete this task.")
        return redirect('employees:task_list')
    
    task.status = 'completed'
    task.completed_date = timezone.now().date()
    task.save()
    
    messages.success(request, 'Task marked as completed.')
    return redirect('employees:task_detail', pk=task.pk)
