import os
import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import Lead, LeadActivity

def import_facebook_leads(user):
    """
    Import leads from Facebook Ads API
    
    Args:
        user: The user initiating the import
        
    Returns:
        int: Number of leads imported
    """
    # Get Facebook API credentials from settings
    app_id = settings.FACEBOOK_APP_ID
    app_secret = settings.FACEBOOK_APP_SECRET
    access_token = settings.FACEBOOK_ACCESS_TOKEN
    
    if not all([app_id, app_secret, access_token]):
        raise ValueError("Facebook API credentials are not properly configured.")
    
    # Get form IDs - for a real implementation, this would be stored in a configuration
    form_ids = ["123456789", "987654321"]  # Replace with actual form IDs
    
    # Set time period for fetching leads (last 7 days)
    since_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    imported_count = 0
    
    # Iterate through form IDs and fetch leads
    for form_id in form_ids:
        endpoint = f"https://graph.facebook.com/v13.0/{form_id}/leads"
        params = {
            'access_token': access_token,
            'fields': 'created_time,id,form_id,field_data',
            'since': since_date
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process leads
            leads = data.get('data', [])
            for lead_data in leads:
                # Check if lead already exists
                fb_lead_id = lead_data.get('id')
                existing_lead = Lead.objects.filter(facebook_lead_id=fb_lead_id).first()
                
                if existing_lead:
                    # Lead already imported, skip
                    continue
                
                # Extract lead info from field_data
                field_data = lead_data.get('field_data', [])
                lead_info = {}
                
                for field in field_data:
                    field_name = field.get('name', '').lower()
                    field_value = field.get('values', [''])[0]
                    
                    if field_name in ['first_name', 'firstname']:
                        lead_info['first_name'] = field_value
                    elif field_name in ['last_name', 'lastname']:
                        lead_info['last_name'] = field_value
                    elif field_name in ['email', 'email_address']:
                        lead_info['email'] = field_value
                    elif field_name in ['phone', 'phone_number']:
                        lead_info['phone'] = field_value
                    elif field_name in ['company', 'company_name']:
                        lead_info['company'] = field_value
                    elif field_name in ['job_title', 'title']:
                        lead_info['job_title'] = field_value
                
                # Create new lead if we have at least email or phone
                if lead_info.get('email') or lead_info.get('phone'):
                    new_lead = Lead(
                        first_name=lead_info.get('first_name', ''),
                        last_name=lead_info.get('last_name', ''),
                        email=lead_info.get('email', ''),
                        phone=lead_info.get('phone', ''),
                        company=lead_info.get('company', ''),
                        job_title=lead_info.get('job_title', ''),
                        status=Lead.NEW,
                        source=Lead.FACEBOOK,
                        facebook_lead_id=fb_lead_id
                    )
                    new_lead.save()
                    
                    # Create activity log
                    LeadActivity.objects.create(
                        lead=new_lead,
                        user=user,
                        activity_type='Imported',
                        description='Lead imported from Facebook Ads'
                    )
                    
                    imported_count += 1
                    
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error connecting to Facebook API: {str(e)}")
    
    return imported_count
