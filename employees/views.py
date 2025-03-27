from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth.models import User
import json
import calendar
import datetime
from .models import Attendance, Salary, EmployeeTask, LeaveApplication
from .forms import (
    AttendanceForm, SalaryForm, PunchForm, EmployeeTaskForm,
    LeaveApplicationForm, LeaveResponseForm
)

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
    
    # Get all employees for the filter dropdown (admins/managers only)
    employees = None
    if user_profile.is_admin or user_profile.is_ops_manager:
        employees = User.objects.all().order_by('username')
    
    context = {
        'attendances': attendances,
        'employees': employees,
        'current_employee': employee_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'employees/attendance_log.html', context)

@login_required
def punch_in(request):
    """Handle employee punch in"""
    # Don't allow admins to punch in/out
    if request.user.userprofile.is_admin:
        messages.warning(request, "Administrators don't need to punch in/out.")
        return redirect('dashboard:index')
        
    today = timezone.now().date()
    current_time = timezone.now().time()
    
    # Check if already punched in today
    try:
        attendance = Attendance.objects.get(employee=request.user, date=today)
        if attendance.punch_in_time:
            messages.warning(request, "You've already punched in today!")
        else:
            # Update the punch in time
            attendance.punch_in_time = current_time
            attendance.save()
            messages.success(request, f"Punched in successfully at {current_time.strftime('%H:%M')}.")
    except Attendance.DoesNotExist:
        # Create new attendance record
        attendance = Attendance.objects.create(
            employee=request.user,
            date=today,
            punch_in_time=current_time,
            status='present'
        )
        messages.success(request, f"Punched in successfully at {current_time.strftime('%H:%M')}.")
    
    # Redirect back to the dashboard
    return redirect('dashboard:index')

@login_required
def punch_out(request):
    """Handle employee punch out"""
    # Don't allow admins to punch in/out
    if request.user.userprofile.is_admin:
        messages.warning(request, "Administrators don't need to punch in/out.")
        return redirect('dashboard:index')
        
    today = timezone.now().date()
    current_time = timezone.now().time()
    
    # Check if punched in today
    try:
        attendance = Attendance.objects.get(employee=request.user, date=today)
        if not attendance.punch_in_time:
            messages.error(request, "You need to punch in first before punching out!")
        elif attendance.punch_out_time:
            messages.warning(request, "You've already punched out today!")
        else:
            # Update the punch out time
            attendance.punch_out_time = current_time
            attendance.save()
            
            # Calculate hours worked
            hours = attendance.hours_worked
            
            if hours < 9:
                messages.warning(request, f"Punched out at {current_time.strftime('%H:%M')}. You've worked {hours:.2f} hours. Daily requirement: 9 hours.")
            else:
                messages.success(request, f"Punched out at {current_time.strftime('%H:%M')}. You've completed your required 9 hours today!")
    except Attendance.DoesNotExist:
        messages.error(request, "You need to punch in first before punching out!")
    
    # Redirect back to the dashboard
    return redirect('dashboard:index')

@login_required
def salary_list(request):
    # Show all salaries for admins/managers, but only own salary for others
    user_profile = request.user.userprofile
    
    # Initialize filter variables
    employee_id = None
    month = None
    year = None
    status = None
    
    if user_profile.is_admin or user_profile.is_ops_manager:
        salaries = Salary.objects.all()
        
        # Filter by employee
        employee_id = request.GET.get('employee')
        if employee_id:
            salaries = salaries.filter(employee_id=employee_id)
        
        # Filter by month
        month = request.GET.get('month')
        if month:
            salaries = salaries.filter(month=month)
        
        # Filter by year
        year = request.GET.get('year')
        if year:
            salaries = salaries.filter(year=year)
        
        # Filter by status
        status = request.GET.get('status')
        if status:
            salaries = salaries.filter(status=status)
    else:
        # Regular employees can only see their own salaries
        salaries = Salary.objects.filter(employee=request.user)
    
    # Order by most recent first
    salaries = salaries.order_by('-year', '-month')
    
    # Get all employees for the filter dropdown (admins/managers only)
    employees = None
    if user_profile.is_admin or user_profile.is_ops_manager:
        employees = User.objects.all().order_by('username')
    
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

# Add a view to calculate salaries
@login_required
def salary_calculate(request, pk):
    """Calculate salary based on attendance records"""
    salary = get_object_or_404(Salary, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to calculate salaries.")
        return redirect('employees:salary_list')
    
    # Calculate and save
    salary.calculate_salary()
    salary.save()
    
    messages.success(request, f"Salary calculated based on {salary.days_present} days present out of {salary.working_days} working days.")
    return redirect('employees:salary_update', pk=salary.pk)

# Attendance Calendar View
@login_required
def attendance_calendar(request):
    """View for calendar view of attendance"""
    # Get year and month from request, default to current
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # Determine which employee's attendance to show
    user_profile = request.user.userprofile
    employee_id = request.GET.get('employee')
    
    if user_profile.is_admin or user_profile.is_ops_manager:
        if employee_id:
            employee = get_object_or_404(User, pk=employee_id)
        else:
            # Default to the first employee
            employee = User.objects.first()
        
        employees = User.objects.all().order_by('username')
    else:
        # Regular employees can only see their own attendance
        employee = request.user
        employees = None
    
    # Get the calendar for the selected month/year
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Get attendance records for the selected month/year
    start_date = datetime.date(year, month, 1)
    # Get the last day of the month
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    
    attendances = Attendance.objects.filter(
        employee=employee,
        date__range=[start_date, end_date]
    )
    
    # Convert to dictionary for easy lookup
    attendance_dict = {attendance.date: attendance for attendance in attendances}
    
    # Get leave applications for this period
    leaves = LeaveApplication.objects.filter(
        employee=employee,
        start_date__lte=end_date,
        end_date__gte=start_date,
        status='approved'
    )
    
    # Create a list of dates that are on approved leave
    leave_dates = []
    for leave in leaves:
        current_date = max(leave.start_date, start_date)
        while current_date <= min(leave.end_date, end_date):
            leave_dates.append(current_date)
            current_date += datetime.timedelta(days=1)
    
    # Convert the calendar data to include attendance status
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                # Day outside current month
                week_data.append({
                    'day': '',
                    'status': None,
                    'is_today': False,
                    'attendance': None,
                    'on_leave': False
                })
            else:
                date = datetime.date(year, month, day)
                attendance = attendance_dict.get(date)
                
                week_data.append({
                    'day': day,
                    'status': attendance.status if attendance else None,
                    'is_today': date == timezone.now().date(),
                    'attendance': attendance,
                    'on_leave': date in leave_dates
                })
        calendar_data.append(week_data)
    
    # Generate month navigation links
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
    
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1
    
    context = {
        'calendar_data': calendar_data,
        'month_name': month_name,
        'year': year,
        'employee': employee,
        'employees': employees,
        'current_employee': employee_id,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    
    return render(request, 'employees/attendance_calendar.html', context)

# Leave Management Views
@login_required
def leave_list(request):
    """List leave applications"""
    user_profile = request.user.userprofile
    
    # Initialize filter variables
    employee_id = None
    status = None
    leave_type = None
    
    if user_profile.is_admin or user_profile.is_ops_manager:
        leaves = LeaveApplication.objects.all()
        
        # Filter by employee
        employee_id = request.GET.get('employee')
        if employee_id:
            leaves = leaves.filter(employee_id=employee_id)
    else:
        # Regular employees can only see their own leaves
        leaves = LeaveApplication.objects.filter(employee=request.user)
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        leaves = leaves.filter(status=status)
    
    # Filter by leave type if specified
    leave_type = request.GET.get('leave_type')
    if leave_type:
        leaves = leaves.filter(leave_type=leave_type)
    
    # Order by application date, most recent first
    leaves = leaves.order_by('-applied_on')
    
    # Get all employees for the filter dropdown (admins/managers only)
    employees = None
    if user_profile.is_admin or user_profile.is_ops_manager:
        employees = User.objects.all().order_by('username')
    
    context = {
        'leaves': leaves,
        'employees': employees,
        'current_employee': employee_id,
        'current_status': status,
        'current_leave_type': leave_type,
        'status_choices': LeaveApplication.STATUS_CHOICES,
        'leave_type_choices': LeaveApplication.LEAVE_TYPE_CHOICES,
    }
    
    return render(request, 'employees/leave_list.html', context)

@login_required
def leave_create(request):
    """Create a new leave application"""
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.save()
            
            messages.success(request, 'Leave application submitted successfully.')
            return redirect('employees:leave_list')
    else:
        form = LeaveApplicationForm()
    
    context = {
        'form': form,
        'is_create': True,
    }
    
    return render(request, 'employees/leave_form.html', context)

@login_required
def leave_detail(request, pk):
    """View details of a leave application"""
    leave = get_object_or_404(LeaveApplication, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager or leave.employee == request.user):
        messages.error(request, "You don't have permission to view this leave application.")
        return redirect('employees:leave_list')
    
    context = {
        'leave': leave,
    }
    
    return render(request, 'employees/leave_detail.html', context)

@login_required
def leave_respond(request, pk):
    """Respond to a leave application (approve/decline)"""
    leave = get_object_or_404(LeaveApplication, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to respond to leave applications.")
        return redirect('employees:leave_list')
    
    if leave.status != 'pending':
        messages.warning(request, "This leave application has already been processed.")
        return redirect('employees:leave_detail', pk=leave.pk)
    
    if request.method == 'POST':
        form = LeaveResponseForm(request.POST, instance=leave)
        if form.is_valid():
            response = form.save(commit=False)
            response.approved_by = request.user
            response.response_date = timezone.now()
            response.save()
            
            if response.status == 'approved':
                messages.success(request, 'Leave application approved successfully.')
            else:
                messages.info(request, 'Leave application has been declined.')
                
            return redirect('employees:leave_detail', pk=leave.pk)
    else:
        form = LeaveResponseForm(instance=leave)
    
    context = {
        'form': form,
        'leave': leave,
    }
    
    return render(request, 'employees/leave_response_form.html', context)

@login_required
def leave_cancel(request, pk):
    """Cancel a leave application"""
    leave = get_object_or_404(LeaveApplication, pk=pk)
    
    # Check permission (only the employee who applied or admin can cancel)
    if not (request.user == leave.employee or request.user.userprofile.is_admin):
        messages.error(request, "You don't have permission to cancel this leave application.")
        return redirect('employees:leave_list')
    
    if leave.status != 'pending' and not request.user.userprofile.is_admin:
        messages.warning(request, "This leave application has already been processed and cannot be cancelled.")
        return redirect('employees:leave_detail', pk=leave.pk)
    
    if request.method == 'POST':
        leave.status = 'cancelled'
        leave.response_date = timezone.now()
        if request.user.userprofile.is_admin:
            leave.approved_by = request.user
        leave.save()
        
        messages.success(request, 'Leave application cancelled successfully.')
        return redirect('employees:leave_list')
    
    context = {
        'leave': leave,
    }
    
    return render(request, 'employees/leave_cancel_confirm.html', context)

# Task Management Views
@login_required
def task_list(request):
    user_profile = request.user.userprofile
    
    # Determine which tasks to show based on user role
    employee_id = request.GET.get('employee')
    
    if user_profile.is_admin or user_profile.is_manager:
        # Admins and managers can see all tasks
        if employee_id:
            # Filter by assigned employee if specified
            tasks = EmployeeTask.objects.filter(assigned_to_id=employee_id)
        else:
            tasks = EmployeeTask.objects.all()
    else:
        # Regular users can see tasks they've been assigned or that they've created
        tasks = EmployeeTask.objects.filter(
            Q(assigned_to=request.user) | Q(assigned_by=request.user)
        )
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)
    
    # Filter by priority if specified
    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)
    
    # Order by priority and due date
    tasks = tasks.order_by('-priority', 'due_date', 'status')
    
    # Get all employees for the filter dropdown (admins/managers only)
    employees = None
    if user_profile.is_admin or user_profile.is_manager:
        employees = User.objects.all().order_by('username')
    
    context = {
        'tasks': tasks,
        'employees': employees,
        'current_employee': employee_id,
        'current_status': status,
        'current_priority': priority,
        'status_choices': EmployeeTask.STATUS_CHOICES,
        'priority_choices': EmployeeTask.PRIORITY_CHOICES,
    }
    
    return render(request, 'employees/task_list.html', context)

@login_required
def task_detail(request, pk):
    task = get_object_or_404(EmployeeTask, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager or task.assigned_to == request.user or task.assigned_by == request.user):
        messages.error(request, "You don't have permission to view this task.")
        return redirect('employees:task_list')
    
    context = {
        'task': task,
    }
    
    return render(request, 'employees/task_detail.html', context)

@login_required
def task_create(request):
    # Everyone can create tasks, but admins/managers can assign to anyone
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