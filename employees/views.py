from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Task, Attendance, Salary
from .forms import TaskForm, AttendanceForm, SalaryForm, TaskFilterForm, EmployeeFilterForm
from accounts.models import UserProfile

@login_required
def employees_list(request):
    """Display list of employees with filtering options"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_manager() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to view employees.")
        return redirect('dashboard:index')
    
    # Initialize filter form
    filter_form = EmployeeFilterForm(request.GET)
    
    # Base queryset
    employees = User.objects.filter(profile__isnull=False)
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        # Filter by role if provided
        role = filter_form.cleaned_data.get('role')
        if role:
            employees = employees.filter(profile__role=role)
            
        # Search by name or email if provided
        search_query = filter_form.cleaned_data.get('search')
        if search_query:
            employees = employees.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query) |
                Q(username__icontains=search_query)
            )
    
    # Pagination
    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'employees': page_obj,
        'filter_form': filter_form,
        'user_profile': user_profile,
    }
    
    return render(request, 'employees/employees_list.html', context)

@login_required
def employee_create(request):
    """Create a new employee (redirects to register page)"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_manager()):
        messages.error(request, "You don't have permission to create employees.")
        return redirect('employees:employees_list')
    
    # Redirect to registration page
    return redirect('accounts:register')

@login_required
def employee_detail(request, pk):
    """View employee details"""
    employee = get_object_or_404(User, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_manager() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to view employee details.")
        return redirect('employees:employees_list')
    
    # Get employee's tasks
    tasks = Task.objects.filter(assigned_to=employee)
    
    # Get employee's attendance records
    attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')[:10]
    
    # Get employee's current salary
    current_salary = Salary.objects.filter(employee=employee).order_by('-effective_date').first()
    
    context = {
        'employee': employee,
        'employee_profile': UserProfile.objects.get(user=employee),
        'tasks': tasks,
        'attendance_records': attendance_records,
        'current_salary': current_salary,
        'user_profile': user_profile,
    }
    
    return render(request, 'employees/employee_detail.html', context)

@login_required
def tasks_list(request):
    """Display list of tasks with filtering options"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Initialize filter form
    filter_form = TaskFilterForm(request.GET)
    
    # Base queryset - filtered by role
    if user_profile.is_developer() or user_profile.is_sales_rep():
        # Regular employees only see their assigned tasks
        tasks = Task.objects.filter(assigned_to=request.user)
    else:
        # Managers, admins, and operations managers see all tasks
        tasks = Task.objects.all()
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        # Filter by status if provided
        status = filter_form.cleaned_data.get('status')
        if status:
            tasks = tasks.filter(status=status)
        
        # Filter by priority if provided
        priority = filter_form.cleaned_data.get('priority')
        if priority:
            tasks = tasks.filter(priority=priority)
            
        # Filter by assigned user if provided
        assigned_to = filter_form.cleaned_data.get('assigned_to')
        if assigned_to:
            tasks = tasks.filter(assigned_to=assigned_to)
            
        # Filter by project if provided
        project = filter_form.cleaned_data.get('project')
        if project:
            tasks = tasks.filter(project=project)
            
        # Search by title or description if provided
        search_query = filter_form.cleaned_data.get('search')
        if search_query:
            tasks = tasks.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
    
    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tasks': page_obj,
        'filter_form': filter_form,
        'user_profile': user_profile,
    }
    
    return render(request, 'employees/tasks_list.html', context)

@login_required
def task_create(request):
    """Create a new task"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_manager() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to create tasks.")
        return redirect('employees:tasks_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, f"Task '{task.title}' created successfully!")
            return redirect('employees:tasks_list')
    else:
        # Pre-fill assigned_to if provided in URL
        employee_id = request.GET.get('employee')
        initial_data = {}
        if employee_id:
            initial_data['assigned_to'] = employee_id
        
        form = TaskForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Create Task',
        'user_profile': user_profile,
    }
    
    return render(request, 'employees/task_form.html', context)

@login_required
def task_update(request, pk):
    """Update an existing task"""
    task = get_object_or_404(Task, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_manager() or user_profile.is_operations_manager() or 
            task.assigned_to == request.user):
        messages.error(request, "You don't have permission to update this task.")
        return redirect('employees:tasks_list')
    
    if request.method == 'POST':
        # Determine which fields can be updated based on role
        if user_profile.is_developer() or user_profile.is_sales_rep():
            # Regular employees can only update status
            form = TaskForm(request.POST, instance=task, fields=['status'])
        else:
            # Managers and admins can update all fields
            form = TaskForm(request.POST, instance=task)
        
        if form.is_valid():
            form.save()
            messages.success(request, f"Task '{task.title}' updated successfully!")
            return redirect('employees:tasks_list')
    else:
        # Determine which fields can be updated based on role
        if user_profile.is_developer() or user_profile.is_sales_rep():
            # Regular employees can only update status
            form = TaskForm(instance=task, fields=['status'])
        else:
            # Managers and admins can update all fields
            form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'title': 'Update Task',
        'user_profile': user_profile,
    }
    
    return render(request, 'employees/task_form.html', context)

@login_required
def task_delete(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_manager() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to delete tasks.")
        return redirect('employees:tasks_list')
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f"Task '{task_title}' deleted successfully!")
        return redirect('employees:tasks_list')
    
    context = {
        'task': task,
        'user_profile': user_profile,
    }
    
    return render(request, 'employees/task_confirm_delete.html', context)

@login_required
def attendance(request):
    """View and manage attendance"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Get today's attendance record for the user
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(employee=request.user, date=today).first()
    
    # Handle check-in/check-out
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'check_in':
            # Create new attendance record for today
            if not today_attendance:
                attendance = Attendance(
                    employee=request.user,
                    date=today,
                    time_in=timezone.now().time()
                )
                attendance.save()
                messages.success(request, "You have successfully checked in.")
            else:
                messages.error(request, "You have already checked in today.")
                
        elif action == 'check_out':
            # Update existing attendance record with check-out time
            if today_attendance and not today_attendance.time_out:
                today_attendance.time_out = timezone.now().time()
                today_attendance.save()
                messages.success(request, "You have successfully checked out.")
            else:
                messages.error(request, "You need to check in first or have already checked out.")
    
    # Get recent attendance records for the current user
    attendance_records = Attendance.objects.filter(employee=request.user).order_by('-date')[:10]
    
    # For admins/managers, get all attendance records for today
    all_today_attendance = None
    if user_profile.is_admin() or user_profile.is_manager() or user_profile.is_operations_manager():
        all_today_attendance = Attendance.objects.filter(date=today).order_by('employee__username')
    
    context = {
        'today_attendance': today_attendance,
        'attendance_records': attendance_records,
        'all_today_attendance': all_today_attendance,
        'user_profile': user_profile,
    }
    
    return render(request, 'employees/attendance.html', context)

@login_required
def salary_list(request):
    """List and manage employee salaries"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to view salary information.")
        return redirect('dashboard:index')
    
    # Get employees and their current salaries
    employees = User.objects.filter(profile__isnull=False)
    employee_salaries = []
    
    for employee in employees:
        current_salary = Salary.objects.filter(employee=employee).order_by('-effective_date').first()
        employee_salaries.append({
            'employee': employee,
            'current_salary': current_salary
        })
    
    context = {
        'employee_salaries': employee_salaries,
        'user_profile': user_profile,
    }
    
    return render(request, 'employees/salary_list.html', context)

@login_required
def salary_create(request):
    """Create a new salary record for an employee"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to create salary records.")
        return redirect('employees:salary_list')
    
    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Salary record created successfully!")
            return redirect('employees:salary_list')
    else:
        # Pre-fill employee if provided in URL
        employee_id = request.GET.get('employee')
        initial_data = {}
        if employee_id:
            initial_data['employee'] = employee_id
            
        form = SalaryForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Create Salary Record',
        'user_profile': user_profile,
    }
    
    return render(request, 'employees/salary_form.html', context)

@login_required
def salary_history(request, employee_id):
    """View salary history for an employee"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to view salary history.")
        return redirect('employees:salary_list')
    
    employee = get_object_or_404(User, pk=employee_id)
    salary_history = Salary.objects.filter(employee=employee).order_by('-effective_date')
    
    context = {
        'employee': employee,
        'salary_history': salary_history,
        'user_profile': user_profile,
    }
    
    return render(request, 'employees/salary_history.html', context)

@login_required
def salary_report(request):
    """Generate monthly salary report"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to view salary reports.")
        return redirect('dashboard:index')
    
    # Get all employees
    employees = User.objects.filter(profile__isnull=False)
    salary_data = []
    total_salary = 0
    
    # Get month and year from request or use current month/year
    month = request.GET.get('month', timezone.now().month)
    year = request.GET.get('year', timezone.now().year)
    
    # Try to convert to integers
    try:
        month = int(month)
        year = int(year)
    except (ValueError, TypeError):
        month = timezone.now().month
        year = timezone.now().year
    
    # Calculate salary for each employee
    for employee in employees:
        # Get salary effective on the first day of the selected month
        report_date = timezone.datetime(year, month, 1).date()
        salary = Salary.objects.filter(
            employee=employee, 
            effective_date__lte=report_date
        ).order_by('-effective_date').first()
        
        if salary:
            total_salary += salary.amount
            salary_data.append({
                'employee': employee,
                'salary': salary
            })
    
    context = {
        'salary_data': salary_data,
        'total_salary': total_salary,
        'month': month,
        'year': year,
        'user_profile': user_profile,
    }
    
    return render(request, 'reports/salary_report.html', context)
