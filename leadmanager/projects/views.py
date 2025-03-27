from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Client, Project, Task, ProjectStatus
from .forms import ClientForm, ProjectForm, TaskForm
from core.utils import can_access


@login_required
def client_list(request):
    if not can_access(request.user, 'clients', 'view'):
        messages.error(request, "You don't have permission to view clients.")
        return redirect('dashboard:index')
    
    clients = Client.objects.all()
    
    # Handle search
    query = request.GET.get('q')
    if query:
        clients = clients.filter(
            Q(name__icontains=query) | 
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )
    
    context = {
        'clients': clients,
        'can_create': can_access(request.user, 'clients', 'create'),
    }
    return render(request, 'projects/clients_list.html', context)


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    if not can_access(request.user, 'clients', 'view'):
        messages.error(request, "You don't have permission to view client details.")
        return redirect('projects:client_list')
    
    # Get projects for this client
    projects = client.projects.all()
    
    context = {
        'client': client,
        'projects': projects,
        'can_update': can_access(request.user, 'clients', 'update'),
    }
    return render(request, 'projects/client_detail.html', context)


@login_required
def client_create(request):
    if not can_access(request.user, 'clients', 'create'):
        messages.error(request, "You don't have permission to create clients.")
        return redirect('projects:client_list')
    
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f"Client '{client.name}' created successfully.")
            return redirect('projects:client_detail', pk=client.pk)
    else:
        form = ClientForm()
    
    return render(request, 'projects/client_form.html', {'form': form, 'title': 'Create Client'})


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    if not can_access(request.user, 'clients', 'update'):
        messages.error(request, "You don't have permission to update clients.")
        return redirect('projects:client_detail', pk=client.pk)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f"Client '{client.name}' updated successfully.")
            return redirect('projects:client_detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'projects/client_form.html', {'form': form, 'client': client, 'title': 'Update Client'})


@login_required
def project_list(request):
    # Filter projects based on user role
    if request.user.profile.role in ['admin', 'operations_manager']:
        projects = Project.objects.all()
    elif request.user.profile.role == 'developer':
        # Developers can see projects they have tasks assigned to
        projects = Project.objects.filter(tasks__assigned_to=request.user).distinct()
    else:
        projects = Project.objects.none()
    
    # Handle search
    query = request.GET.get('q')
    if query:
        projects = projects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(client__name__icontains=query)
        )
    
    # Handle filters
    status_filter = request.GET.get('status')
    if status_filter:
        projects = projects.filter(status__id=status_filter)
    
    # Get filter options
    statuses = ProjectStatus.objects.all()
    
    context = {
        'projects': projects,
        'statuses': statuses,
        'can_create': can_access(request.user, 'projects', 'create'),
    }
    return render(request, 'projects/projects_list.html', context)


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user can view this project
    can_view = False
    if request.user.profile.role in ['admin', 'operations_manager']:
        can_view = True
    elif request.user.profile.role == 'developer' and project.tasks.filter(assigned_to=request.user).exists():
        can_view = True
    
    if not can_view:
        messages.error(request, "You don't have permission to view this project.")
        return redirect('projects:project_list')
    
    # Get tasks for this project
    tasks = project.tasks.all()
    
    context = {
        'project': project,
        'tasks': tasks,
        'can_update': can_access(request.user, 'projects', 'update'),
        'can_create_task': can_access(request.user, 'tasks', 'create'),
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_create(request):
    if not can_access(request.user, 'projects', 'create'):
        messages.error(request, "You don't have permission to create projects.")
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f"Project '{project.name}' created successfully.")
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/project_form.html', {'form': form, 'title': 'Create Project'})


@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if not can_access(request.user, 'projects', 'update'):
        messages.error(request, "You don't have permission to update projects.")
        return redirect('projects:project_detail', pk=project.pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"Project '{project.name}' updated successfully.")
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/project_form.html', {'form': form, 'project': project, 'title': 'Update Project'})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user can view this task
    can_view = False
    if request.user.profile.role in ['admin', 'operations_manager']:
        can_view = True
    elif request.user.profile.role == 'developer' and task.assigned_to == request.user:
        can_view = True
    
    if not can_view:
        messages.error(request, "You don't have permission to view this task.")
        return redirect('projects:project_list')
    
    context = {
        'task': task,
        'can_update': can_access(request.user, 'tasks', 'update') or task.assigned_to == request.user,
    }
    return render(request, 'projects/task_detail.html', context)


@login_required
def task_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    if not can_access(request.user, 'tasks', 'create'):
        messages.error(request, "You don't have permission to create tasks.")
        return redirect('projects:project_detail', pk=project.pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            messages.success(request, f"Task '{task.name}' created successfully.")
            return redirect('projects:project_detail', pk=project.pk)
    else:
        # Pre-select the project
        form = TaskForm(user=request.user, initial={'project': project})
    
    return render(request, 'projects/task_form.html', {'form': form, 'project': project, 'title': 'Create Task'})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user can update this task
    can_update = False
    if request.user.profile.role in ['admin', 'operations_manager']:
        can_update = True
    elif request.user.profile.role == 'developer' and task.assigned_to == request.user:
        can_update = True
    
    if not can_update:
        messages.error(request, "You don't have permission to update this task.")
        return redirect('projects:task_detail', pk=task.pk)
    
    if request.method == 'POST':
        # For developers, only allow updating the status
        if request.user.profile.role == 'developer':
            # Only update the status field
            task.status = request.POST.get('status')
            task.save()
            messages.success(request, f"Task status updated successfully.")
            return redirect('projects:task_detail', pk=task.pk)
        else:
            form = TaskForm(request.POST, instance=task, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, f"Task '{task.name}' updated successfully.")
                return redirect('projects:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    return render(request, 'projects/task_form.html', {
        'form': form, 
        'task': task, 
        'title': 'Update Task',
        'is_developer': request.user.profile.role == 'developer'
    })
