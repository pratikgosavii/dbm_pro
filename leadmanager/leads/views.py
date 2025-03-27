from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
import pandas as pd
import datetime
import os
from io import BytesIO

from .models import Lead, LeadSource, LeadStatus
from .forms import LeadForm, LeadImportForm, LeadAssignForm, FacebookLeadFetchForm
from core.utils import handle_excel_upload, fetch_facebook_leads, can_access


@login_required
def lead_list(request):
    # Filter leads based on user role
    if request.user.profile.role in ['admin', 'manager']:
        leads = Lead.objects.all()
    elif request.user.profile.role == 'sales_rep':
        leads = Lead.objects.filter(assigned_to=request.user)
    else:
        leads = Lead.objects.none()
    
    # Handle search
    query = request.GET.get('q')
    if query:
        leads = leads.filter(
            Q(name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(phone__icontains=query) |
            Q(company__icontains=query)
        )
    
    # Handle filters
    status_filter = request.GET.get('status')
    if status_filter:
        leads = leads.filter(status__id=status_filter)
    
    source_filter = request.GET.get('source')
    if source_filter:
        leads = leads.filter(source__id=source_filter)
    
    # Get filter options
    statuses = LeadStatus.objects.all()
    sources = LeadSource.objects.all()
    
    context = {
        'leads': leads,
        'statuses': statuses,
        'sources': sources,
        'can_create': can_access(request.user, 'leads', 'create'),
        'can_import': can_access(request.user, 'leads', 'import'),
        'can_export': can_access(request.user, 'leads', 'export'),
        'can_assign': can_access(request.user, 'leads', 'assign'),
    }
    return render(request, 'leads/leads_list.html', context)


@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    # Check if user can view this lead
    if not can_access(request.user, 'leads', 'view') or \
       (request.user.profile.role == 'sales_rep' and lead.assigned_to != request.user):
        messages.error(request, "You don't have permission to view this lead.")
        return redirect('leads:lead_list')
    
    context = {
        'lead': lead,
        'can_update': can_access(request.user, 'leads', 'update'),
    }
    return render(request, 'leads/lead_detail.html', context)


@login_required
def lead_create(request):
    if not can_access(request.user, 'leads', 'create'):
        messages.error(request, "You don't have permission to create leads.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        form = LeadForm(request.POST, user=request.user)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by = request.user
            lead.save()
            messages.success(request, f"Lead '{lead.name}' created successfully.")
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = LeadForm(user=request.user)
    
    return render(request, 'leads/lead_form.html', {'form': form, 'title': 'Create Lead'})


@login_required
def lead_update(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    # Check if user can update this lead
    if not can_access(request.user, 'leads', 'update') or \
       (request.user.profile.role == 'sales_rep' and lead.assigned_to != request.user):
        messages.error(request, "You don't have permission to update this lead.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lead '{lead.name}' updated successfully.")
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = LeadForm(instance=lead, user=request.user)
    
    return render(request, 'leads/lead_form.html', {'form': form, 'lead': lead, 'title': 'Update Lead'})


@login_required
def lead_import(request):
    if not can_access(request.user, 'leads', 'import'):
        messages.error(request, "You don't have permission to import leads.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        form = LeadImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            source = form.cleaned_data['source']
            
            # Process the file
            data, error = handle_excel_upload(excel_file)
            
            if error:
                messages.error(request, error)
            else:
                # Create default status
                default_status, _ = LeadStatus.objects.get_or_create(name='New')
                
                # Create leads from data
                leads_created = 0
                leads_skipped = 0
                
                for item in data:
                    # Required fields
                    name = item.get('name') or item.get('Name')
                    email = item.get('email') or item.get('Email')
                    
                    if not name or not email:
                        leads_skipped += 1
                        continue
                    
                    # Optional fields
                    phone = item.get('phone') or item.get('Phone', '')
                    company = item.get('company') or item.get('Company', '')
                    job_title = item.get('job_title') or item.get('Job Title', '')
                    notes = item.get('notes') or item.get('Notes', '')
                    
                    # Create lead
                    Lead.objects.create(
                        name=name,
                        email=email,
                        phone=phone,
                        company=company,
                        job_title=job_title,
                        notes=notes,
                        source=source,
                        status=default_status,
                        created_by=request.user
                    )
                    leads_created += 1
                
                messages.success(request, f"{leads_created} leads imported successfully. {leads_skipped} leads skipped.")
                return redirect('leads:lead_list')
    else:
        form = LeadImportForm()
    
    return render(request, 'leads/lead_import.html', {'form': form})


@login_required
def lead_export(request):
    if not can_access(request.user, 'leads', 'export'):
        messages.error(request, "You don't have permission to export leads.")
        return redirect('leads:lead_list')
    
    # Filter leads based on user role
    if request.user.profile.role in ['admin', 'manager']:
        leads = Lead.objects.all()
    elif request.user.profile.role == 'sales_rep':
        leads = Lead.objects.filter(assigned_to=request.user)
    else:
        leads = Lead.objects.none()
    
    # Prepare data for export
    data = []
    for lead in leads:
        data.append({
            'Name': lead.name,
            'Email': lead.email,
            'Phone': lead.phone or '',
            'Company': lead.company or '',
            'Job Title': lead.job_title or '',
            'Source': lead.source.name if lead.source else '',
            'Status': lead.status.name if lead.status else '',
            'Assigned To': f"{lead.assigned_to.first_name} {lead.assigned_to.last_name}" if lead.assigned_to else '',
            'Created At': lead.created_at.strftime('%Y-%m-%d %H:%M'),
            'Notes': lead.notes or ''
        })
    
    # Create Excel file
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Leads')
    
    # Prepare response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=leads_export_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx'
    
    return response


@login_required
def lead_assign(request):
    if not can_access(request.user, 'leads', 'assign'):
        messages.error(request, "You don't have permission to assign leads.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        form = LeadAssignForm(request.POST)
        if form.is_valid():
            leads = form.cleaned_data['leads']
            assigned_to = form.cleaned_data['assigned_to']
            
            # Assign leads
            count = 0
            for lead in leads:
                lead.assigned_to = assigned_to
                lead.save()
                count += 1
            
            messages.success(request, f"{count} leads assigned to {assigned_to.first_name} {assigned_to.last_name}.")
            return redirect('leads:lead_list')
    else:
        # Limit to unassigned leads for initial form
        form = LeadAssignForm()
    
    return render(request, 'leads/lead_assign.html', {'form': form})


@login_required
def facebook_leads(request):
    if not can_access(request.user, 'leads', 'import'):
        messages.error(request, "You don't have permission to import leads from Facebook.")
        return redirect('leads:lead_list')
    
    if request.method == 'POST':
        form = FacebookLeadFetchForm(request.POST)
        if form.is_valid():
            ad_account = form.cleaned_data['ad_account']
            days = form.cleaned_data['days']
            
            # Fetch leads from Facebook
            data, error = fetch_facebook_leads()
            
            if error:
                messages.error(request, error)
            else:
                # Process the leads (simplified for demonstration)
                source, _ = LeadSource.objects.get_or_create(name='Facebook Ads')
                default_status, _ = LeadStatus.objects.get_or_create(name='New')
                
                # Count for user feedback
                leads_created = 0
                
                messages.success(request, f"{leads_created} leads imported from Facebook Ads.")
                return redirect('leads:lead_list')
    else:
        form = FacebookLeadFetchForm()
    
    return render(request, 'leads/facebook_leads.html', {'form': form})
