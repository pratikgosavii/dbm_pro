import os
import pandas as pd
import requests
from django.conf import settings


def handle_excel_upload(excel_file):
    """
    Process uploaded Excel file and return data as a list of dictionaries
    """
    try:
        if excel_file.name.endswith('.xlsx'):
            df = pd.read_excel(excel_file)
        elif excel_file.name.endswith('.csv'):
            df = pd.read_csv(excel_file)
        else:
            return None, "Unsupported file format. Please upload .xlsx or .csv files."
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict('records')
        return data, None
    except Exception as e:
        return None, f"Error processing file: {str(e)}"


def export_to_excel(data, filename):
    """
    Export data to Excel file
    """
    try:
        df = pd.DataFrame(data)
        return df.to_excel(filename, index=False)
    except Exception as e:
        return None, f"Error exporting to Excel: {str(e)}"


def fetch_facebook_leads():
    """
    Fetch leads from Facebook Ads API
    """
    try:
        access_token = settings.FACEBOOK_ACCESS_TOKEN
        if not access_token:
            return None, "Facebook access token not configured"
        
        # This is a simplified example. In real implementation, you'd need proper API endpoints and paging
        url = f"https://graph.facebook.com/v15.0/me/adaccounts?fields=name,leads&access_token={access_token}"
        
        response = requests.get(url)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error fetching leads: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Error connecting to Facebook API: {str(e)}"


def can_access(user, resource_type, action=None):
    """
    Check if a user has permission to access a resource or perform an action
    """
    if not user.is_authenticated:
        return False
    
    role = user.profile.role
    
    # Admin can do everything
    if role == 'admin':
        return True
    
    # Define permissions for different roles
    permissions = {
        'manager': {
            'leads': ['view', 'create', 'update', 'assign', 'import', 'export'],
            'employees': ['view'],
            'reports': ['view'],
        },
        'sales_rep': {
            'leads': ['view', 'update'],
        },
        'operations_manager': {
            'projects': ['view', 'create', 'update', 'assign'],
            'clients': ['view', 'create', 'update'],
            'payments': ['view', 'create', 'update'],
            'reports': ['view'],
        },
        'developer': {
            'projects': ['view'],
            'tasks': ['view', 'update'],
        }
    }
    
    # Check if role has any permissions for resource_type
    if role in permissions and resource_type in permissions[role]:
        # If action is specified, check if it's allowed
        if action:
            return action in permissions[role][resource_type]
        # If no action is specified, user has some permissions for resource_type
        return True
    
    return False
