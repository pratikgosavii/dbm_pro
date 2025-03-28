from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Lead, LeadSource, LeadStatus
from .forms import LeadForm, LeadAssignForm, ExcelImportForm
from .facebook_api import import_facebook_leads
from .excel_utils import export_leads_to_excel, import_leads_from_excel
import datetime

@login_required
def lead_list(request):
    # Determine which leads to show based on user role
    user_profile = request.user.userprofile
    
    if user_profile.is_admin or user_profile.is_manager:
        leads = Lead.objects.all()
    elif user_profile.is_sales_rep:
        leads = Lead.objects.filter(assigned_to=request.user)
    else:
        leads = Lead.objects.none()
    
    # Filter by search query
    query = request.GET.get('q')
    if query:
        leads = leads.filter(
            Q(name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(phone__icontains=query) | 
            Q(company__icontains=query)
        )
    
    # Filter by status
    status_id = request.GET.get('status')
    if status_id:
        if status_id == 'unassigned':
            leads = leads.filter(status__isnull=True)
        else:
            try:
                status_id_int = int(status_id)
                leads = leads.filter(status_id=status_id_int)
            except ValueError:
                # In case of invalid status_id, just ignore the filter
                pass
    
    # Filter by source
    source_id = request.GET.get('source')
    if source_id:
        leads = leads.filter(source_id=source_id)
    
    # Get filter options
    statuses = LeadStatus.objects.filter(is_active=True)
    sources = LeadSource.objects.filter(is_active=True)
    
    context = {
        'leads': leads,
        'statuses': statuses,
        'sources': sources,
        'current_status': status_id,
        'current_source': source_id,
        'query': query,
    }
    
    return render(request, 'leads/lead_list.html', context)

@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager or 
            (user_profile.is_sales_rep and lead.assigned_to == request.user)):
        messages.error(request, "You don't have permission to view this lead.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead updated successfully.')
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = LeadForm(instance=lead)
    
    context = {
        'lead': lead,
        'form': form,
    }
    
    return render(request, 'leads/lead_detail.html', context)

@login_required
def lead_create(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager or user_profile.is_sales_rep):
        messages.error(request, "You don't have permission to create leads.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by = request.user
            lead.save()
            messages.success(request, 'Lead created successfully.')
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = LeadForm()
    
    context = {
        'form': form,
        'is_create': True,
    }
    
    return render(request, 'leads/lead_form.html', context)

@login_required
def lead_update(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager or 
            (user_profile.is_sales_rep and lead.assigned_to == request.user)):
        messages.error(request, "You don't have permission to update this lead.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead updated successfully.')
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = LeadForm(instance=lead)
    
    context = {
        'form': form,
        'lead': lead,
        'is_create': False,
    }
    
    return render(request, 'leads/lead_form.html', context)

@login_required
def lead_assign(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager):
        messages.error(request, "You don't have permission to assign leads.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        form = LeadAssignForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead assigned successfully.')
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = LeadAssignForm(instance=lead)
    
    context = {
        'form': form,
        'lead': lead,
    }
    
    return render(request, 'leads/lead_form.html', context)

@login_required
def lead_export(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager):
        messages.error(request, "You don't have permission to export leads.")
        return redirect('leads:lead_list')
    
    # Get leads based on filters
    leads = Lead.objects.all()
    
    # Filter by status
    status_id = request.GET.get('status')
    if status_id:
        if status_id == 'unassigned':
            leads = leads.filter(status__isnull=True)
        else:
            try:
                status_id_int = int(status_id)
                leads = leads.filter(status_id=status_id_int)
            except ValueError:
                # In case of invalid status_id, just ignore the filter
                pass
    
    # Filter by source
    source_id = request.GET.get('source')
    if source_id:
        leads = leads.filter(source_id=source_id)
    
    # Generate Excel file
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    filename = f'leads_export_{datetime.datetime.now().strftime("%Y-%m-%d")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    export_leads_to_excel(leads, response)
    
    return response

@login_required
def lead_import(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager):
        messages.error(request, "You don't have permission to import leads.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                imported_count = import_leads_from_excel(excel_file, request.user)
                messages.success(request, f'{imported_count} leads imported successfully.')
                return redirect('leads:lead_list')
            except Exception as e:
                messages.error(request, f'Error importing leads: {str(e)}')
    else:
        form = ExcelImportForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'leads/lead_import.html', context)

@login_required
def facebook_leads_import(request):
    # Check permission
    user_profile = request.user.userprofile
    if not (user_profile.is_admin or user_profile.is_manager):
        messages.error(request, "You don't have permission to import Facebook leads.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        try:
            if not settings.FACEBOOK_ACCESS_TOKEN:
                messages.error(request, "Facebook access token is not configured. Please set up your Facebook API credentials.")
                return redirect('leads:lead_list')
                
            imported_count = import_facebook_leads(request.user)
            if imported_count == 0:
                messages.warning(request, 'No new leads found to import from Facebook.')
            else:
                messages.success(request, f'{imported_count} leads imported from Facebook.')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Unexpected error while importing leads: {str(e)}')
        return redirect('leads:lead_list')
    
    return render(request, 'leads/lead_facebook_import.html')
