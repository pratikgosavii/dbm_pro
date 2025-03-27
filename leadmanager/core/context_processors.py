def role_context(request):
    """
    Add user role to the template context for all templates.
    """
    context = {}
    if request.user.is_authenticated:
        context['user_role'] = request.user.profile.role
    return context
