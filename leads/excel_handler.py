import pandas as pd
import io
from django.utils import timezone
from django.db import transaction
from .models import Lead, LeadSource, LeadStatus

def import_leads_from_excel(excel_file, user):
    """
    Import leads from Excel file
    
    Args:
        excel_file: Excel file uploaded by the user
        user: User performing the import
        
    Returns:
        dict: Results of the import operation
    """
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        # Validate required columns
        required_columns = ['name']
        for column in required_columns:
            if column not in df.columns:
                return {
                    'success': False,
                    'error': f"Missing required column: {column}",
                    'count': 0
                }
        
        # Get default lead source and status
        excel_source, _ = LeadSource.objects.get_or_create(name='Excel Import')
        default_status = LeadStatus.objects.first()
        
        # Start a transaction to ensure all leads are imported or none
        with transaction.atomic():
            count = 0
            
            for _, row in df.iterrows():
                # Skip if name is empty
                if pd.isna(row['name']) or row['name'] == '':
                    continue
                
                # Extract lead data
                lead_data = {
                    'name': row['name'],
                    'email': row.get('email', '') if not pd.isna(row.get('email', '')) else '',
                    'phone': str(row.get('phone', '')) if not pd.isna(row.get('phone', '')) else '',
                    'company': row.get('company', '') if not pd.isna(row.get('company', '')) else '',
                    'notes': row.get('notes', '') if not pd.isna(row.get('notes', '')) else '',
                    'source': excel_source,
                    'status': default_status,
                    'created_by': user
                }
                
                # Create lead
                Lead.objects.create(**lead_data)
                count += 1
        
        return {
            'success': True,
            'count': count,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'count': 0
        }

def export_leads_to_excel(output, leads):
    """
    Export leads to Excel file
    
    Args:
        output: HttpResponse or other file-like object
        leads: QuerySet of leads to export
        
    Returns:
        None: Writes Excel data to the output stream
    """
    # Create DataFrame from leads
    data = []
    
    for lead in leads:
        data.append({
            'ID': lead.id,
            'Name': lead.name,
            'Email': lead.email or '',
            'Phone': lead.phone or '',
            'Company': lead.company or '',
            'Status': lead.status.name if lead.status else '',
            'Source': lead.source.name if lead.source else '',
            'Assigned To': lead.assigned_to.get_full_name() if lead.assigned_to else '',
            'Created At': lead.created_at,
            'Notes': lead.notes or ''
        })
    
    df = pd.DataFrame(data)
    
    # Write DataFrame to Excel
    df.to_excel(output, index=False)
    
    return output
