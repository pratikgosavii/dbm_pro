import pandas as pd
from io import BytesIO
from .models import Lead, LeadSource, LeadStatus

def export_leads_to_excel(leads_queryset, output):
    """
    Export leads to Excel
    
    Args:
        leads_queryset: The queryset of leads to export
        output: A file-like object to write the Excel data to
    """
    # Create a pandas DataFrame from the leads queryset
    data = []
    
    for lead in leads_queryset:
        data.append({
            'ID': lead.pk,
            'Name': lead.name,
            'Email': lead.email or '',
            'Phone': lead.phone or '',
            'Company': lead.company or '',
            'Source': lead.source.name if lead.source else '',
            'Status': lead.status.name if lead.status else '',
            'Assigned To': lead.assigned_to.get_full_name() if lead.assigned_to else '',
            'Notes': lead.notes or '',
            'Created At': lead.created_at.strftime('%Y-%m-%d %H:%M'),
            'Updated At': lead.updated_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    df = pd.DataFrame(data)
    
    # Write the DataFrame to Excel
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Leads', index=False)
        
        # Adjust column widths
        worksheet = writer.sheets['Leads']
        for i, col in enumerate(df.columns):
            max_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_width)

def import_leads_from_excel(excel_file, user):
    """
    Import leads from Excel file
    
    Args:
        excel_file: The uploaded Excel file
        user: The user importing the leads
        
    Returns:
        int: The number of leads imported
    """
    # Read the Excel file
    df = pd.read_excel(excel_file)
    
    # Validate required columns
    required_columns = ['Name', 'Email', 'Phone']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Prepare source and status mappings
    sources = {source.name.lower(): source for source in LeadSource.objects.all()}
    statuses = {status.name.lower(): status for status in LeadStatus.objects.all()}
    
    # Import leads
    imported_count = 0
    
    for _, row in df.iterrows():
        # Skip if name is missing
        if pd.isna(row['Name']):
            continue
        
        # Get or create source if provided
        source = None
        if 'Source' in df.columns and not pd.isna(row['Source']):
            source_name = row['Source'].lower()
            source = sources.get(source_name)
            
            if not source:
                source = LeadSource.objects.create(name=row['Source'])
                sources[source_name] = source
        
        # Get or create status if provided
        status = None
        if 'Status' in df.columns and not pd.isna(row['Status']):
            status_name = row['Status'].lower()
            status = statuses.get(status_name)
            
            if not status:
                status = LeadStatus.objects.create(name=row['Status'])
                statuses[status_name] = status
        
        # Create the lead
        lead = Lead.objects.create(
            name=row['Name'],
            email=row['Email'] if not pd.isna(row['Email']) else None,
            phone=row['Phone'] if not pd.isna(row['Phone']) else None,
            company=row['Company'] if 'Company' in df.columns and not pd.isna(row['Company']) else None,
            source=source,
            status=status,
            notes=row['Notes'] if 'Notes' in df.columns and not pd.isna(row['Notes']) else None,
            created_by=user
        )
        
        imported_count += 1
    
    return imported_count
