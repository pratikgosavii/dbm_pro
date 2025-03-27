from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Client, Project, Payment
from .forms import ClientForm, ProjectForm, PaymentForm, ProjectFilterForm, PaymentFilterForm
from accounts.models import UserProfile

@login_required
def clients_list(request):
    """Display list of clients"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to view clients.")
        return redirect('dashboard:index')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        clients = Client.objects.filter(
            Q(name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    else:
        clients = Client.objects.all()
    
    # Pagination
    paginator = Paginator(clients, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'clients': page_obj,
        'search_query': search_query,
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/clients_list.html', context)

@login_required
def client_create(request):
    """Create a new client"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to create clients.")
        return redirect('projects:clients_list')
    
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f"Client {client.name} created successfully!")
            return redirect('projects:clients_list')
    else:
        form = ClientForm()
    
    context = {
        'form': form,
        'title': 'Create Client',
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/client_form.html', context)

@login_required
def client_update(request, pk):
    """Update an existing client"""
    client = get_object_or_404(Client, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to update clients.")
        return redirect('projects:clients_list')
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f"Client {client.name} updated successfully!")
            return redirect('projects:clients_list')
    else:
        form = ClientForm(instance=client)
    
    context = {
        'form': form,
        'client': client,
        'title': 'Update Client',
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/client_form.html', context)

@login_required
def client_delete(request, pk):
    """Delete a client"""
    client = get_object_or_404(Client, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to delete clients.")
        return redirect('projects:clients_list')
    
    if request.method == 'POST':
        client_name = client.name
        client.delete()
        messages.success(request, f"Client {client_name} deleted successfully!")
        return redirect('projects:clients_list')
    
    context = {
        'client': client,
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/client_confirm_delete.html', context)

@login_required
def projects_list(request):
    """Display list of projects with filtering options"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Initialize filter form
    filter_form = ProjectFilterForm(request.GET)
    
    # Base queryset - filtered by role
    if user_profile.is_developer():
        # Developers only see their assigned projects
        projects = Project.objects.filter(assigned_developers=request.user)
    else:
        # Others see all projects
        projects = Project.objects.all()
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        # Filter by status if provided
        status = filter_form.cleaned_data.get('status')
        if status:
            projects = projects.filter(status=status)
        
        # Filter by client if provided
        client = filter_form.cleaned_data.get('client')
        if client:
            projects = projects.filter(client=client)
            
        # Filter by developer if provided
        developer = filter_form.cleaned_data.get('developer')
        if developer:
            projects = projects.filter(assigned_developers=developer)
            
        # Search by name or description if provided
        search_query = filter_form.cleaned_data.get('search')
        if search_query:
            projects = projects.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
    
    # Pagination
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'projects': page_obj,
        'filter_form': filter_form,
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/projects_list.html', context)

@login_required
def project_create(request):
    """Create a new project"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to create projects.")
        return redirect('projects:projects_list')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f"Project {project.name} created successfully!")
            return redirect('projects:projects_list')
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'title': 'Create Project',
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/project_form.html', context)

@login_required
def project_update(request, pk):
    """Update an existing project"""
    project = get_object_or_404(Project, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to update projects.")
        return redirect('projects:projects_list')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"Project {project.name} updated successfully!")
            return redirect('projects:projects_list')
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'title': 'Update Project',
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/project_form.html', context)

@login_required
def project_delete(request, pk):
    """Delete a project"""
    project = get_object_or_404(Project, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to delete projects.")
        return redirect('projects:projects_list')
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f"Project {project_name} deleted successfully!")
        return redirect('projects:projects_list')
    
    context = {
        'project': project,
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/project_confirm_delete.html', context)

@login_required
def project_detail(request, pk):
    """View project details, including payments"""
    project = get_object_or_404(Project, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions - developers can only view their assigned projects
    if user_profile.is_developer() and request.user not in project.assigned_developers.all():
        messages.error(request, "You don't have permission to view this project.")
        return redirect('projects:projects_list')
    
    # Get payments for this project
    payments = Payment.objects.filter(project=project)
    
    context = {
        'project': project,
        'payments': payments,
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/project_detail.html', context)

@login_required
def payments_list(request):
    """Display list of payments with filtering options"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to view payments.")
        return redirect('dashboard:index')
    
    # Initialize filter form
    filter_form = PaymentFilterForm(request.GET)
    
    # Base queryset
    payments = Payment.objects.all()
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        # Filter by project if provided
        project = filter_form.cleaned_data.get('project')
        if project:
            payments = payments.filter(project=project)
        
        # Filter by payment method if provided
        payment_method = filter_form.cleaned_data.get('payment_method')
        if payment_method:
            payments = payments.filter(payment_method=payment_method)
            
        # Filter by date range if provided
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        
        if start_date:
            payments = payments.filter(payment_date__gte=start_date)
        
        if end_date:
            payments = payments.filter(payment_date__lte=end_date)
    
    # Pagination
    paginator = Paginator(payments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate total payments
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'payments': page_obj,
        'filter_form': filter_form,
        'total_payments': total_payments,
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/payments_list.html', context)

@login_required
def payment_create(request):
    """Create a new payment"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to create payments.")
        return redirect('projects:payments_list')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.save()
            messages.success(request, "Payment recorded successfully!")
            return redirect('projects:payments_list')
    else:
        # Pre-fill project ID if provided in URL
        project_id = request.GET.get('project')
        initial_data = {}
        if project_id:
            initial_data['project'] = project_id
        
        form = PaymentForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Record Payment',
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/payment_form.html', context)

@login_required
def payment_update(request, pk):
    """Update an existing payment"""
    payment = get_object_or_404(Payment, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to update payments.")
        return redirect('projects:payments_list')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment updated successfully!")
            return redirect('projects:payments_list')
    else:
        form = PaymentForm(instance=payment)
    
    context = {
        'form': form,
        'payment': payment,
        'title': 'Update Payment',
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/payment_form.html', context)

@login_required
def payment_delete(request, pk):
    """Delete a payment"""
    payment = get_object_or_404(Payment, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check permissions
    if not (user_profile.is_admin() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to delete payments.")
        return redirect('projects:payments_list')
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, "Payment deleted successfully!")
        return redirect('projects:payments_list')
    
    context = {
        'payment': payment,
        'user_profile': user_profile,
    }
    
    return render(request, 'projects/payment_confirm_delete.html', context)
