from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Client, Project, ProjectStatus
from .forms import ClientForm, ProjectForm, ProjectAssignForm

@login_required
def client_list(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to view clients.")
        return redirect('dashboard:index')
    
    # Get clients with search filter
    clients = Client.objects.all()
    query = request.GET.get('q')
    if query:
        clients = clients.filter(
            Q(name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(phone__icontains=query) | 
            Q(company__icontains=query)
        )
    
    context = {
        'clients': clients,
        'query': query,
    }
    
    return render(request, 'projects/client_list.html', context)

@login_required
def client_create(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to create clients.")
        return redirect('projects:client_list')
    
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.created_by = request.user
            client.save()
            messages.success(request, 'Client created successfully.')
            return redirect('projects:client_list')
    else:
        form = ClientForm()
    
    context = {
        'form': form,
        'is_create': True,
    }
    
    return render(request, 'projects/client_form.html', context)

@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to update clients.")
        return redirect('projects:client_list')
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client updated successfully.')
            return redirect('projects:client_list')
    else:
        form = ClientForm(instance=client)
    
    context = {
        'form': form,
        'client': client,
        'is_create': False,
    }
    
    return render(request, 'projects/client_form.html', context)

@login_required
def project_list(request):
    # Determine which projects to show based on user role
    user_profile = request.user.userprofile
    
    if user_profile.is_admin or user_profile.is_ops_manager:
        projects = Project.objects.all()
    elif user_profile.is_developer:
        projects = request.user.assigned_projects.all()
    else:
        # Other roles don't see projects
        messages.error(request, "You don't have permission to view projects.")
        return redirect('dashboard:index')
    
    # Filter by search query
    query = request.GET.get('q')
    if query:
        projects = projects.filter(
            Q(name__icontains=query) | 
            Q(client__name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Filter by status
    status_id = request.GET.get('status')
    if status_id:
        projects = projects.filter(status_id=status_id)
    
    # Get filter options
    statuses = ProjectStatus.objects.filter(is_active=True)
    
    context = {
        'projects': projects,
        'statuses': statuses,
        'current_status': status_id,
        'query': query,
    }
    
    return render(request, 'projects/project_list.html', context)

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager or 
            (user_profile.is_developer and request.user in project.assigned_developers.all())):
        messages.error(request, "You don't have permission to view this project.")
        return redirect('projects:project_list')
    
    context = {
        'project': project,
    }
    
    return render(request, 'projects/project_detail.html', context)

@login_required
def project_create(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to create projects.")
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            # Save many-to-many relationships
            form.save_m2m()
            messages.success(request, 'Project created successfully.')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'is_create': True,
    }
    
    return render(request, 'projects/project_form.html', context)

@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to update projects.")
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'is_create': False,
    }
    
    return render(request, 'projects/project_form.html', context)

@login_required
def project_assign(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_ops_manager):
        messages.error(request, "You don't have permission to assign developers to projects.")
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = ProjectAssignForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Developers assigned successfully.')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectAssignForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
    }
    
    return render(request, 'projects/project_form.html', context)
