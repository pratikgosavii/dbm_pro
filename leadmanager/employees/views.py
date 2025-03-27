from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.contrib.auth.models import User
import datetime

from .models import Employee, TimeRecord, Department
from .forms import EmployeeForm, TimeRecordForm, PunchInForm, PunchOutForm, TimesheetFilterForm
from core.models import UserProfile
from core.utils import can_access


@login_required
def employee_list(request):
    if not can_access(request.user, 'employees', 'view'):
        messages.error(request, "You don't have permission to view employees.")
        return redirect('dashboard:index')
    
    employees = Employee.objects.all()
    
    # Handle search
    query = request.GET.get('q')
    if query:
        employees = employees.filter(
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query) | 
            Q(user__email__icontains=query) |
            Q(position__icontains=query)
        )
    
    # Handle filters
    department_filter = request.GET.get('department')
    if department_filter:
        employees = employees.filter(department__id=department_filter)
    
    # Get filter options
    departments = Department.objects.all()
    
    context = {
        'employees': employees,
        'departments': departments,
        'can_create': can_access(request.user, 'employees', 'create'),
    }
    return render(request, 'employees/employees_list.html', context)


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if not can_access(request.user, 'employees', 'view') and employee.user != request.user:
        messages.error(request, "You don't have permission to view employee details.")
        return redirect('employees:employee_list')
    
    # Get recent time records
    time_records = employee.time_records.order_by('-date')[:10]
    
    context = {
        'employee': employee,
        'time_records': time_records,
        'can_update': can_access(request.user, 'employees', 'update') or employee.user == request.user,
    }
    return render(request, 'employees/employee_detail.html', context)


@login_required
def employee_create(request):
    if not can_access(request.user, 'employees', 'create'):
        messages.error(request, "You don't have permission to create employees.")
        return redirect('employees:employee_list')
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            # Get or create user
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            
            # Create username from email
            username = email.split('@')[0]
            
            # Check if username exists, append numbers if needed
            base_username = username
            count = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{count}"
                count += 1
            
            # Create user with random password
            user = User.objects.create_user(
                username=username,
                email=email,
                password=User.objects.make_random_password(),
                first_name=first_name,
                last_name=last_name
            )
            
            # Create employee
            employee = form.save(commit=False)
            employee.user = user
            employee.save()
            
            messages.success(request, f"Employee '{employee.full_name}' created successfully.")
            return redirect('employees:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Create Employee'})


@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if not can_access(request.user, 'employees', 'update') and employee.user != request.user:
        messages.error(request, "You don't have permission to update this employee.")
        return redirect('employees:employee_detail', pk=employee.pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee, instance_user=employee.user)
        if form.is_valid():
            # Update user details
            user = employee.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            # Update employee
            form.save()
            
            messages.success(request, f"Employee '{employee.full_name}' updated successfully.")
            return redirect('employees:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee, instance_user=employee.user)
    
    return render(request, 'employees/employee_form.html', {'form': form, 'employee': employee, 'title': 'Update Employee'})


@login_required
def timesheet(request, employee_id=None):
    # If employee_id is provided, show timesheet for specific employee
    # Otherwise, show timesheet based on user role
    if employee_id:
        employee = get_object_or_404(Employee, pk=employee_id)
        if not can_access(request.user, 'employees', 'view') and employee.user != request.user:
            messages.error(request, "You don't have permission to view this timesheet.")
            return redirect('dashboard:index')
    else:
        # For regular users, show their own timesheet
        if not request.user.profile.role in ['admin', 'operations_manager']:
            try:
                employee = request.user.employee
            except Employee.DoesNotExist:
                messages.error(request, "You don't have an employee profile.")
                return redirect('dashboard:index')
        else:
            # Admin can see all timesheets
            employee = None
    
    # Get time records
    if employee:
        records = TimeRecord.objects.filter(employee=employee)
    else:
        records = TimeRecord.objects.all()
    
    # Handle filtering
    filter_form = TimesheetFilterForm(request.GET)
    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        filter_employee = filter_form.cleaned_data.get('employee')
        
        if start_date:
            records = records.filter(date__gte=start_date)
        
        if end_date:
            records = records.filter(date__lte=end_date)
        
        if filter_employee and not employee:
            records = records.filter(employee=filter_employee)
    
    # Calculate total hours
    total_hours = sum(record.hours_worked or 0 for record in records)
    
    # For admins, add the employee filter options
    if not employee and request.user.profile.role in ['admin', 'operations_manager']:
        employees = Employee.objects.all()
    else:
        employees = None
    
    context = {
        'records': records,
        'employee': employee,
        'total_hours': total_hours,
        'filter_form': filter_form,
        'employees': employees,
    }
    return render(request, 'employees/timesheet.html', context)


@login_required
def punch_in(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "You don't have an employee profile.")
        return redirect('dashboard:index')
    
    # Check if already punched in today
    today = datetime.date.today()
    existing_record = TimeRecord.objects.filter(employee=employee, date=today).first()
    
    if existing_record and existing_record.time_in:
        messages.warning(request, "You have already punched in today.")
        return redirect('employees:timesheet')
    
    if request.method == 'POST':
        form = PunchInForm(request.POST)
        if form.is_valid():
            # Create new time record or update existing
            if not existing_record:
                existing_record = TimeRecord(employee=employee, date=today)
            
            existing_record.time_in = datetime.datetime.now().time()
            existing_record.notes = form.cleaned_data['notes']
            existing_record.save()
            
            messages.success(request, f"Punched in successfully at {existing_record.time_in.strftime('%H:%M')}.")
            return redirect('employees:timesheet')
    else:
        form = PunchInForm()
    
    return render(request, 'employees/punch_in.html', {'form': form})


@login_required
def punch_out(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "You don't have an employee profile.")
        return redirect('dashboard:index')
    
    # Check if punched in today
    today = datetime.date.today()
    existing_record = TimeRecord.objects.filter(employee=employee, date=today).first()
    
    if not existing_record or not existing_record.time_in:
        messages.warning(request, "You haven't punched in today.")
        return redirect('employees:timesheet')
    
    if existing_record.time_out:
        messages.warning(request, "You have already punched out today.")
        return redirect('employees:timesheet')
    
    if request.method == 'POST':
        form = PunchOutForm(request.POST)
        if form.is_valid():
            existing_record.time_out = datetime.datetime.now().time()
            
            # Append notes if provided
            if form.cleaned_data['notes']:
                if existing_record.notes:
                    existing_record.notes += f"\n\nPunch out notes: {form.cleaned_data['notes']}"
                else:
                    existing_record.notes = form.cleaned_data['notes']
            
            existing_record.save()
            
            messages.success(request, f"Punched out successfully at {existing_record.time_out.strftime('%H:%M')}.")
            return redirect('employees:timesheet')
    else:
        form = PunchOutForm()
    
    return render(request, 'employees/punch_out.html', {'form': form})


@login_required
def salary_report(request):
    if not can_access(request.user, 'reports', 'view'):
        messages.error(request, "You don't have permission to view salary reports.")
        return redirect('dashboard:index')
    
    # Get all employees
    employees = Employee.objects.all()
    
    # Handle filtering
    month = request.GET.get('month', datetime.date.today().month)
    year = request.GET.get('year', datetime.date.today().year)
    
    try:
        month = int(month)
        year = int(year)
    except (ValueError, TypeError):
        month = datetime.date.today().month
        year = datetime.date.today().year
    
    # Calculate working days in month
    import calendar
    num_days = calendar.monthrange(year, month)[1]
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, num_days)
    
    # Calculate business days (excluding weekends)
    business_days = 0
    for i in range(num_days):
        day = start_date + datetime.timedelta(days=i)
        if day.weekday() < 5:  # 0-4 are Monday to Friday
            business_days += 1
    
    # Calculate salary details for each employee
    employee_data = []
    for employee in employees:
        # Get time records for this month
        time_records = TimeRecord.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calculate total hours worked
        total_hours = sum(record.hours_worked or 0 for record in time_records)
        
        # Calculate days worked
        days_worked = time_records.values('date').distinct().count()
        
        # Calculate daily rate
        daily_rate = employee.salary / business_days if business_days > 0 else 0
        
        # Calculate amount earned
        earned = daily_rate * days_worked
        
        employee_data.append({
            'employee': employee,
            'total_hours': total_hours,
            'days_worked': days_worked,
            'business_days': business_days,
            'daily_rate': daily_rate,
            'earned': earned,
        })
    
    # Get month and year options for filter
    import calendar
    month_options = [(i, calendar.month_name[i]) for i in range(1, 13)]
    current_year = datetime.date.today().year
    year_options = range(current_year - 2, current_year + 1)
    
    context = {
        'employee_data': employee_data,
        'month': month,
        'year': year,
        'month_options': month_options,
        'year_options': year_options,
        'month_name': calendar.month_name[month],
    }
    return render(request, 'reports/salary_report.html', context)
