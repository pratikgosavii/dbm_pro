import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import Lead, LeadSource

def import_facebook_leads(user):
    """
    Import leads from Facebook Ads API
    Returns the number of imported leads
    """
    app_id = settings.FACEBOOK_APP_ID
    app_secret = settings.FACEBOOK_APP_SECRET
    access_token = settings.FACEBOOK_ACCESS_TOKEN

    if not all([app_id, app_secret, access_token]):
        raise ValueError("Facebook API credentials are not properly configured")

    # Get or create the Facebook source
    facebook_source, _ = LeadSource.objects.get_or_create(name='Facebook Ads')

    # Calculate date range for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Format dates for Facebook API
    since = int(start_date.timestamp())

    # Get leads from Facebook
    url = f"https://graph.facebook.com/v18.0/me/leads"
    params = {
        'access_token': access_token,
        'since': since,
        'fields': 'id,created_time,field_data'
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'error' in data:
        raise ValueError(f"Facebook API error: {data['error'].get('message', 'Unknown error')}")

    imported_count = 0
    leads = data.get('data', [])

    for lead in leads:
        facebook_lead_id = lead.get('id')

        # Skip if lead already exists
        if Lead.objects.filter(facebook_lead_id=facebook_lead_id).exists():
            continue

        field_data = {
            field['name']: field['values'][0] 
            for field in lead.get('field_data', [])
            if field.get('values')
        }

        # Create new lead
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