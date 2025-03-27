from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import LoginForm, UserProfileForm, EmployeeCreationForm, EmployeeCategoryForm
from .models import UserProfile, EmployeeCategory

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def employee_create(request):
    """View to create a new employee"""
    # Check if user has permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to create employees.")
        return redirect('employees:employee_list')
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.is_staff = form.cleaned_data['role'] in ['admin', 'ops_manager']
            user.save()
            
            # Update user profile
            user.userprofile.role = form.cleaned_data['role']
            user.userprofile.category = form.cleaned_data['category']
            user.userprofile.phone = form.cleaned_data['phone']
            user.userprofile.address = form.cleaned_data['address']
            user.userprofile.profile_picture = form.cleaned_data['profile_picture']
            user.userprofile.save()
            
            messages.success(request, f"Employee '{user.username}' created successfully!")
            return redirect('employees:employee_detail', pk=user.id)
    else:
        form = EmployeeCreationForm()
    
    return render(request, 'accounts/employee_form.html', {'form': form, 'is_create': True})

@login_required
def employee_category_list(request):
    """View to list all employee categories"""
    # Check if user has permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to view employee categories.")
        return redirect('employees:employee_list')
    
    categories = EmployeeCategory.objects.all().order_by('name')
    
    return render(request, 'accounts/employee_category_list.html', {'categories': categories})

@login_required
def employee_category_create(request):
    """View to create a new employee category"""
    # Check if user has permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to create categories.")
        return redirect('employees:employee_list')
    
    if request.method == 'POST':
        form = EmployeeCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' created successfully!")
            return redirect('accounts:employee_category_list')
    else:
        form = EmployeeCategoryForm()
    
    return render(request, 'accounts/employee_category_form.html', {'form': form, 'is_create': True})
