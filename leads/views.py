from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Lead, LeadActivity
from .forms import LeadForm, LeadImportForm, LeadFilterForm
from .facebook_api import import_facebook_leads
from .excel_utils import import_leads_from_excel, export_leads_to_excel
from accounts.models import UserProfile

@login_required
def leads_list(request):
    """Display list of leads with filtering options"""
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    
    # Initialize filter form
    filter_form = LeadFilterForm(request.GET)
    
    # Base queryset - filtered by role
    if user_profile.is_sales_rep():
        # Sales reps only see their assigned leads
        leads = Lead.objects.filter(assigned_to=user)
    else:
        # Managers, admins, and operations managers see all leads
        leads = Lead.objects.all()
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        # Filter by status if provided
        status = filter_form.cleaned_data.get('status')
        if status:
            leads = leads.filter(status=status)
        
        # Filter by source if provided
        source = filter_form.cleaned_data.get('source')
        if source:
            leads = leads.filter(source=source)
            
        # Filter by assigned user if provided
        assigned_to = filter_form.cleaned_data.get('assigned_to')
        if assigned_to:
            leads = leads.filter(assigned_to=assigned_to)
            
        # Search by name, email, or company if provided
        search_query = filter_form.cleaned_data.get('search')
        if search_query:
            leads = leads.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query) | 
                Q(company__icontains=search_query)
            )
    
    # Pagination
    paginator = Paginator(leads, 10)  # Show 10 leads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'leads': page_obj,
        'filter_form': filter_form,
        'user_profile': user_profile,
    }
    
    return render(request, 'leads/leads_list.html', context)

@login_required
def lead_create(request):
    """Create a new lead"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check if user has permission to create leads
    if not (user_profile.is_admin() or user_profile.is_manager() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to create leads.")
        return redirect('leads:list')
    
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = Lead.MANUAL
            lead.save()
            
            # Create activity log
            LeadActivity.objects.create(
                lead=lead,
                user=request.user,
                activity_type='Created',
                description='Lead was created manually'
            )
            
            messages.success(request, f"Lead {lead.full_name} created successfully!")
            return redirect('leads:list')
    else:
        form = LeadForm()
    
    context = {
        'form': form,
        'title': 'Create Lead',
        'user_profile': user_profile,
    }
    
    return render(request, 'leads/lead_form.html', context)

@login_required
def lead_update(request, pk):
    """Update an existing lead"""
    lead = get_object_or_404(Lead, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check if user has permission to update this lead
    if not (user_profile.is_admin() or user_profile.is_manager() or user_profile.is_operations_manager() or 
            (user_profile.is_sales_rep() and lead.assigned_to == request.user)):
        messages.error(request, "You don't have permission to update this lead.")
        return redirect('leads:list')
    
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            old_status = lead.status
            updated_lead = form.save()
            
            # Create activity log for status change
            if old_status != updated_lead.status:
                LeadActivity.objects.create(
                    lead=updated_lead,
                    user=request.user,
                    activity_type='Status Changed',
                    description=f'Status updated from {old_status} to {updated_lead.status}'
                )
            
            messages.success(request, f"Lead {updated_lead.full_name} updated successfully!")
            return redirect('leads:list')
    else:
        form = LeadForm(instance=lead)
    
    context = {
        'form': form,
        'lead': lead,
        'title': 'Update Lead',
        'user_profile': user_profile,
    }
    
    return render(request, 'leads/lead_form.html', context)

@login_required
def lead_delete(request, pk):
    """Delete a lead"""
    lead = get_object_or_404(Lead, pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check if user has permission to delete leads
    if not (user_profile.is_admin() or user_profile.is_manager()):
        messages.error(request, "You don't have permission to delete leads.")
        return redirect('leads:list')
    
    if request.method == 'POST':
        lead_name = lead.full_name
        lead.delete()
        messages.success(request, f"Lead {lead_name} deleted successfully!")
        return redirect('leads:list')
    
    context = {
        'lead': lead,
        'user_profile': user_profile,
    }
    
    return render(request, 'leads/lead_confirm_delete.html', context)

@login_required
def import_leads(request):
    """Import leads from Excel or Facebook Ads"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check if user has permission to import leads
    if not (user_profile.is_admin() or user_profile.is_manager()):
        messages.error(request, "You don't have permission to import leads.")
        return redirect('leads:list')
    
    if request.method == 'POST':
        form = LeadImportForm(request.POST, request.FILES)
        if form.is_valid():
            import_type = form.cleaned_data.get('import_type')
            
            if import_type == 'excel' and request.FILES.get('excel_file'):
                try:
                    excel_file = request.FILES['excel_file']
                    imported_count = import_leads_from_excel(excel_file, request.user)
                    messages.success(request, f"Successfully imported {imported_count} leads from Excel.")
                    return redirect('leads:list')
                except Exception as e:
                    messages.error(request, f"Error importing leads from Excel: {str(e)}")
            
            elif import_type == 'facebook':
                try:
                    imported_count = import_facebook_leads(request.user)
                    messages.success(request, f"Successfully imported {imported_count} leads from Facebook Ads.")
                    return redirect('leads:list')
                except Exception as e:
                    messages.error(request, f"Error importing leads from Facebook: {str(e)}")
    else:
        form = LeadImportForm()
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    
    return render(request, 'leads/import_leads.html', context)

@login_required
def export_leads(request):
    """Export leads to Excel"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check if user has permission to export leads
    if not (user_profile.is_admin() or user_profile.is_manager() or user_profile.is_operations_manager()):
        messages.error(request, "You don't have permission to export leads.")
        return redirect('leads:list')
    
    # Get filtered queryset (use same filtering logic as in leads_list view)
    filter_form = LeadFilterForm(request.GET)
    
    # Base queryset - filtered by role
    if user_profile.is_sales_rep():
        # Sales reps only see their assigned leads
        leads = Lead.objects.filter(assigned_to=request.user)
    else:
        # Managers, admins, and operations managers see all leads
        leads = Lead.objects.all()
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        # Filter by status if provided
        status = filter_form.cleaned_data.get('status')
        if status:
            leads = leads.filter(status=status)
        
        # Filter by source if provided
        source = filter_form.cleaned_data.get('source')
        if source:
            leads = leads.filter(source=source)
            
        # Filter by assigned user if provided
        assigned_to = filter_form.cleaned_data.get('assigned_to')
        if assigned_to:
            leads = leads.filter(assigned_to=assigned_to)
            
        # Search by name, email, or company if provided
        search_query = filter_form.cleaned_data.get('search')
        if search_query:
            leads = leads.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query) | 
                Q(company__icontains=search_query)
            )
    
    # Create Excel file
    excel_file = export_leads_to_excel(leads)
    
    # Create HTTP response with Excel file
    response = HttpResponse(
        excel_file,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=leads_export.xlsx'
    
    return response
