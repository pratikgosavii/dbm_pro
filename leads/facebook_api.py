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

    try:
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
            error_msg = data['error'].get('message', 'Unknown error')
            if 'invalid_token' in error_msg.lower():
                raise ValueError("Facebook access token is invalid or expired. Please check your configuration.")
            elif 'permission' in error_msg.lower():
                raise ValueError("Missing required Facebook permissions. Please check app permissions.")
            else:
                raise ValueError(f"Facebook API error: {error_msg}")

        imported_count = 0
        leads = data.get('data', [])

        for lead in leads:
            facebook_lead_id = lead.get('id')

            # Skip if lead already exists
            if Lead.objects.filter(facebook_lead_id=facebook_lead_id).exists():
                continue

            # Process field data
            name = None
            email = None
            phone = None
            company = None

            for field in lead.get('field_data', []):
                field_name = field.get('name', '').lower()
                field_value = field.get('values', [''])[0] if field.get('values') else ''

                if 'full_name' in field_name or field_name == 'name':
                    name = field_value
                elif 'email' in field_name:
                    email = field_value
                elif 'phone' in field_name:
                    phone = field_value
                elif 'company' in field_name:
                    company = field_value

            # Create new lead with default name if none found
            Lead.objects.create(
                name=name or 'Unknown Lead',
                email=email,
                phone=phone,
                company=company,
                source=facebook_source,
                facebook_lead_id=facebook_lead_id,
                created_by=user
            )
            imported_count += 1

        return imported_count

    except Exception as e:
        raise ValueError(f"Error importing leads: {str(e)}")