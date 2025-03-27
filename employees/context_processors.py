from django.utils import timezone
from .models import Attendance

def attendance_processor(request):
    """
    Context processor to add today's attendance information to the template context
    """
    context = {}
    
    if request.user.is_authenticated and not request.user.userprofile.is_admin:
        today = timezone.now().date()
        try:
            today_attendance = Attendance.objects.get(
                employee=request.user,
                date=today
            )
            context['today_attendance'] = today_attendance
        except Attendance.DoesNotExist:
            context['today_attendance'] = None
    
    return context