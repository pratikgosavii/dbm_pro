from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages


class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_authenticated:
            # Exclude some URLs from role validation
            excluded_paths = [
                reverse('accounts:logout'),
                '/admin/',
                reverse('dashboard:index'),
            ]
            current_path = request.path
            
            # Check if the current path is in the excluded paths
            if not any(current_path.startswith(path) for path in excluded_paths):
                # Role-based restriction logic
                user_role = request.user.profile.role
                
                # Define role-restricted paths
                admin_paths = ['/employees/manage/']
                manager_paths = ['/leads/assign/']
                ops_manager_paths = ['/projects/manage/', '/payments/manage/']
                
                # Check restrictions
                if current_path.startswith(tuple(admin_paths)) and user_role != 'admin':
                    messages.error(request, "You don't have permission to access this page.")
                    return redirect('dashboard:index')
                
                if current_path.startswith(tuple(manager_paths)) and user_role not in ['admin', 'manager']:
                    messages.error(request, "You don't have permission to access this page.")
                    return redirect('dashboard:index')
                
                if current_path.startswith(tuple(ops_manager_paths)) and user_role not in ['admin', 'operations_manager']:
                    messages.error(request, "You don't have permission to access this page.")
                    return redirect('dashboard:index')
        
        response = self.get_response(request)
        return response
