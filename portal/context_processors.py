from .models import Student, Teacher


def student_context(request):
    """Makes `current_student` / `current_teacher` available in every
    template, so the sidebar can show the logged-in person's name without
    every view needing to fetch and pass it separately."""
    if not request.user.is_authenticated:
        return {}

    context = {}
    try:
        context["current_student"] = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        pass
    try:
        context["current_teacher"] = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        pass
    return context
