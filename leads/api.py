import requests
import datetime
from django.conf import settings
from .models import Lead

def get_facebook_access_token():
    """
    Get access token from environment or settings.
    In production, this should use a more secure method.
    """
    return settings.FACEBOOK_ACCESS_TOKEN

def sync_facebook_leads(ad_account_id, days_back=7):
    """
    Sync leads from Facebook Lead Ads.
    
    Args:
        ad_account_id (str): The Facebook Ad Account ID
        days_back (int): Number of days to look back for leads
        
    Returns:
        dict: Results of the sync operation
    """
    access_token = get_facebook_access_token()
    
    if not access_token:
        raise Exception("Facebook access token not available")
    
    # Calculate date range
    today = datetime.datetime.now()
    since_date = today - datetime.timedelta(days=days_back)
    since_timestamp = int(since_date.timestamp())
    
    # Get forms from the ad account
    forms_url = f"https://graph.facebook.com/v18.0/{ad_account_id}/leadgen_forms"
    forms_params = {
        'access_token': access_token,
    }
    
    forms_response = requests.get(forms_url, params=forms_params)
    forms_data = forms_response.json()
    
    if 'error' in forms_data:
        error_message = forms_data.get('error', {}).get('message', 'Unknown error')
        raise Exception(f"Facebook API error: {error_message}")
    
    forms = forms_data.get('data', [])
    
    imported_count = 0
    skipped_count = 0
    
    # Process each form
    for form in forms:
        form_id = form['id']
        
        # Get leads for this form
        leads_url = f"https://graph.facebook.com/v18.0/{form_id}/leads"
        leads_params = {
            'access_token': access_token,
            'since': since_timestamp,
        }
        
        leads_response = requests.get(leads_url, params=leads_params)
        leads_data = leads_response.json()
        
        if 'error' in leads_data:
            continue  # Skip this form if there's an error
        
        facebook_leads = leads_data.get('data', [])
        
        for fb_lead in facebook_leads:
            lead_id = fb_lead.get('id')
            
            # Check if lead already exists
            if Lead.objects.filter(facebook_lead_id=lead_id).exists():
                skipped_count += 1
                continue
            
            # Extract lead data
            field_data = fb_lead.get('field_data', [])
            
            # Process lead fields
            lead_info = {
                'name': '',
                'email': '',
                'phone': '',
                'company': '',
            }
            
            for field in field_data:
                name = field.get('name', '').lower()
                value = field.get('values', [''])[0] if field.get('values') else ''
                
                if 'name' in name:
                    lead_info['name'] = value
                elif 'email' in name:
                    lead_info['email'] = value
                elif 'phone' in name or 'mobile' in name:
                    lead_info['phone'] = value
                elif 'company' in name or 'organization' in name:
                    lead_info['company'] = value
            
            # Only import if we have at least a name and email
            if lead_info['name'] and lead_info['email']:
                Lead.objects.create(
                    name=lead_info['name'],
                    email=lead_info['email'],
                    phone=lead_info['phone'],
                    company=lead_info['company'],
                    source='facebook',
                    status='new',
                    facebook_lead_id=lead_id
                )
                imported_count += 1
    
    return {
        'imported': imported_count,
        'skipped': skipped_count
    }
