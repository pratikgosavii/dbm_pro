
import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import Lead, LeadSource

def import_facebook_leads(user):
    """
    Import leads from Facebook Ads API
    Returns the number of imported leads
    """
    try:
        # Get Facebook credentials
        app_id = settings.FACEBOOK_APP_ID
        app_secret = settings.FACEBOOK_APP_SECRET
        access_token = settings.FACEBOOK_ACCESS_TOKEN

        if not all([app_id, app_secret, access_token]):
            raise ValueError("Facebook API credentials are not properly configured")

        # Get or create Facebook source
        facebook_source, _ = LeadSource.objects.get_or_create(name='Facebook Ads')

        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        since = int(start_date.timestamp())

        # Make API request
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
            print(f"Facebook API Error: {error_msg}")  # Debug logging
            if 'access token' in error_msg.lower():
                raise ValueError("Invalid Facebook access token. Please check your credentials.")
            raise ValueError(f"Facebook API error: {error_msg}")

        imported_count = 0
        leads = data.get('data', [])

        for lead in leads:
            lead_id = lead.get('id')
            
            # Skip existing leads
            if Lead.objects.filter(facebook_lead_id=lead_id).exists():
                continue

            # Extract lead data
            field_data = {}
            for field in lead.get('field_data', []):
                field_name = field.get('name', '').lower()
                values = field.get('values', [])
                if values:
                    field_data[field_name] = values[0]

            # Create lead
            Lead.objects.create(
                name=field_data.get('full_name', field_data.get('name', 'Unknown Lead')),
                email=field_data.get('email', ''),
                phone=field_data.get('phone_number', field_data.get('phone', '')),
                company=field_data.get('company_name', field_data.get('company', '')),
                source=facebook_source,
                facebook_lead_id=lead_id,
                created_by=user
            )
            imported_count += 1

        return imported_count

    except requests.exceptions.RequestException as e:
        print(f"Network Error: {str(e)}")  # Debug logging
        raise ValueError("Network error while connecting to Facebook API")
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")  # Debug logging
        raise ValueError(f"Error importing leads: {str(e)}")
