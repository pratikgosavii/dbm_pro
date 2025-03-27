import os
import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import Lead, LeadSource

def import_facebook_leads(user):
    """
    Import leads from Facebook Ads API
    Returns the number of imported leads
    """
    
    # Get Facebook API credentials from settings
    app_id = settings.FACEBOOK_APP_ID
    app_secret = settings.FACEBOOK_APP_SECRET
    access_token = settings.FACEBOOK_ACCESS_TOKEN
    
    if not all([app_id, app_secret, access_token]):
        raise ValueError("Facebook API credentials are not properly configured")
    
    # Get or create the Facebook source
    facebook_source, _ = LeadSource.objects.get_or_create(name='Facebook Ads')
    
    # Define the API endpoint
    # For demo purposes, we're just importing leads from a single form
    # In production, you'd want to get all lead forms for your ad account
    
    # Get date range for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Format dates for Facebook API
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Make the API request
    # This is a simplified version - in production you would need proper error handling
    # and potentially pagination for large numbers of leads
    
    # For demonstration purposes, we'll simulate getting leads from the API
    # In a real application, this would be a real API call

    # Simulated leads data
    leads_data = [
        {
            "id": "fb_lead_12345",
            "created_time": "2023-01-01T10:00:00+0000",
            "field_data": [
                {"name": "full_name", "values": ["John Doe"]},
                {"name": "email", "values": ["john.doe@example.com"]},
                {"name": "phone_number", "values": ["1234567890"]},
                {"name": "company_name", "values": ["ABC Corp"]}
            ]
        },
        {
            "id": "fb_lead_67890",
            "created_time": "2023-01-02T11:00:00+0000",
            "field_data": [
                {"name": "full_name", "values": ["Jane Smith"]},
                {"name": "email", "values": ["jane.smith@example.com"]},
                {"name": "phone_number", "values": ["0987654321"]},
                {"name": "company_name", "values": ["XYZ Inc"]}
            ]
        }
    ]
    
    # Process the leads
    imported_count = 0
    
    for lead_data in leads_data:
        # Check if lead already exists to avoid duplicates
        facebook_lead_id = lead_data.get('id')
        
        if Lead.objects.filter(facebook_lead_id=facebook_lead_id).exists():
            continue
        
        # Extract lead fields
        field_data = {field['name']: field['values'][0] for field in lead_data.get('field_data', [])}
        
        # Create the lead
        Lead.objects.create(
            name=field_data.get('full_name', 'Unknown'),
            email=field_data.get('email'),
            phone=field_data.get('phone_number'),
            company=field_data.get('company_name'),
            source=facebook_source,
            facebook_lead_id=facebook_lead_id,
            created_by=user
        )
        
        imported_count += 1
    
    return imported_count
