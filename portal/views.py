from functools import wraps

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from .forms import SignUpForm, AddAssignmentForm, CreateCourseForm, GradeSubmissionForm
from .models import Student, Teacher, Course, Enrollment, Assignment, ScheduleSlot, Submission


def _get_student(user):
    """Small helper: look up the Student record for the logged-in user."""
    return get_object_or_404(Student, user=user)


def _get_teacher(user):
    """Small helper: look up the Teacher record for the logged-in user."""
    return get_object_or_404(Teacher, user=user)


def student_required(view_func):
    """Sends non-student accounts (e.g. a teacher who typed a student URL)
    to their own dashboard instead of throwing a 404."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not Student.objects.filter(user=request.user).exists():
            if Teacher.objects.filter(user=request.user).exists():
                messages.info(request, "That page is for student accounts. Here's your teacher dashboard instead.")
                return redirect("teacher_dashboard")
            messages.error(request, "Your account isn't set up as a student or teacher yet.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


def teacher_required(view_func):
    """Sends non-teacher accounts (e.g. a student who typed /teacher/) to
    their own dashboard instead of throwing a 404."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not Teacher.objects.filter(user=request.user).exists():
            if Student.objects.filter(user=request.user).exists():
                messages.info(request, "That page is for teacher accounts. Here's your student dashboard instead.")
                return redirect("dashboard")
            messages.error(request, "Your account isn't set up as a student or teacher yet.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


# =========================================================
# AUTH: signup + post-login redirect
# =========================================================

def signup(request):
    """Create a new User + a Student or Teacher profile (based on the
    chosen role), then log them straight in."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data["role"]
            extra = form.cleaned_data.get("major_or_department", "")

            if role == "teacher":
                Teacher.objects.create(user=user, teacher_id=f"T-{user.id:05d}", department=extra)
            else:
                Student.objects.create(user=user, student_id=f"ID-{user.id:05d}", major=extra)

            login(request, user)
            messages.success(request, "Account created. Welcome!")
            return redirect("post_login")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def post_login(request):
    """Sends a just-logged-in user to the right home page for their role."""
    if Teacher.objects.filter(user=request.user).exists():
        return redirect("teacher_dashboard")
    return redirect("dashboard")


# =========================================================
# STUDENT PAGES
# =========================================================

@login_required
@student_required
def dashboard(request):
    student = _get_student(request.user)
    enrollments = student.enrollments.select_related("course")

    course_ids = enrollments.values_list("course_id", flat=True)
    assignments = Assignment.objects.filter(course_id__in=course_ids)[:5]

    if enrollments:
        avg_attendance = sum(e.attendance_percent for e in enrollments) // len(enrollments)
    else:
        avg_attendance = 0
    total_credits = sum(e.course.credits for e in enrollments)

    context = {
        "student": student,
        "enrollments": enrollments,
        "assignments": assignments,
        "avg_attendance": avg_attendance,
        "total_credits": total_credits,
    }
    return render(request, "portal/dashboard.html", context)


@login_required
@student_required
def courses(request):
    student = _get_student(request.user)
    enrollments = student.enrollments.select_related("course", "course__teacher__user")

    enrolled_course_ids = enrollments.values_list("course_id", flat=True)
    available_courses = Course.objects.exclude(id__in=enrolled_course_ids).select_related("teacher__user")

    return render(request, "portal/courses.html", {
        "enrollments": enrollments,
        "available_courses": available_courses,
    })


@login_required
@student_required
def enroll_course(request, course_id):
    student = _get_student(request.user)
    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.get_or_create(student=student, course=course)
    messages.success(request, f"Enrolled in {course.code} - {course.title}.")
    return redirect("courses")


@login_required
@student_required
def drop_course(request, enrollment_id):
    student = _get_student(request.user)
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=student)
    course_name = f"{enrollment.course.code}"
    enrollment.delete()
    messages.success(request, f"Dropped {course_name}.")
    return redirect("courses")


@login_required
@student_required
def grades(request):
    student = _get_student(request.user)
    enrollments = student.enrollments.select_related("course")
    return render(request, "portal/grades.html", {"enrollments": enrollments})


@login_required
@student_required
def attendance(request):
    student = _get_student(request.user)
    enrollments = student.enrollments.select_related("course")
    return render(request, "portal/attendance.html", {"enrollments": enrollments})


@login_required
@student_required
def schedule(request):
    student = _get_student(request.user)
    course_ids = student.enrollments.values_list("course_id", flat=True)
    slots = ScheduleSlot.objects.filter(course_id__in=course_ids).select_related("course").order_by("time", "day")
    return render(request, "portal/schedule.html", {"slots": slots})


@login_required
@student_required
def profile(request):
    student = _get_student(request.user)
    return render(request, "portal/profile.html", {"student": student})


@login_required
@student_required
def assignments(request):
    student = _get_student(request.user)
    course_ids = student.enrollments.values_list("course_id", flat=True)
    assignment_list = Assignment.objects.filter(course_id__in=course_ids).select_related("course")

    my_submissions = {
        s.assignment_id: s for s in Submission.objects.filter(student=student)
    }

    rows = [
        {"assignment": a, "submission": my_submissions.get(a.id)}
        for a in assignment_list
    ]

    return render(request, "portal/assignments.html", {"rows": rows})


@login_required
@student_required
def submit_assignment(request, assignment_id):
    student = _get_student(request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.method == "POST":
        defaults = {"content": request.POST.get("content", "")}
        uploaded_file = request.FILES.get("file")
        if uploaded_file:
            defaults["file"] = uploaded_file

        Submission.objects.update_or_create(
            assignment=assignment, student=student, defaults=defaults
        )
        messages.success(request, f"Submitted: {assignment.title}")

    return redirect("assignments")


# =========================================================
# TEACHER PAGES
# =========================================================

@login_required
@teacher_required
def teacher_dashboard(request):
    teacher = _get_teacher(request.user)
    courses_taught = teacher.courses.all()

    course_stats = [
        {"course": c, "student_count": c.enrollment_set.count(), "assignment_count": c.assignment_set.count()}
        for c in courses_taught
    ]

    return render(request, "portal/teacher_dashboard.html", {
        "teacher": teacher,
        "course_stats": course_stats,
        "create_course_form": CreateCourseForm(),
    })


@login_required
@teacher_required
def create_course(request):
    teacher = _get_teacher(request.user)

    if request.method == "POST":
        form = CreateCourseForm(request.POST)
        if form.is_valid():
            Course.objects.create(
                code=form.cleaned_data["code"],
                title=form.cleaned_data["title"],
                credits=form.cleaned_data["credits"],
                teacher=teacher,
            )
            messages.success(request, "Course created.")
        else:
            messages.error(request, "Couldn't create that course - check the fields below.")

    return redirect("teacher_dashboard")


@login_required
@teacher_required
def teacher_course_detail(request, course_id):
    teacher = _get_teacher(request.user)
    course = get_object_or_404(Course, id=course_id, teacher=teacher)

    if request.method == "POST":
        # Updating one student's progress/attendance/grade for this course
        enrollment_id = request.POST.get("enrollment_id")
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, course=course)
        enrollment.progress_percent = request.POST.get("progress_percent", enrollment.progress_percent)
        enrollment.attendance_percent = request.POST.get("attendance_percent", enrollment.attendance_percent)
        enrollment.grade = request.POST.get("grade", enrollment.grade)
        enrollment.save()
        messages.success(request, f"Updated {enrollment.student}.")
        return redirect("teacher_course_detail", course_id=course.id)

    roster = course.enrollment_set.select_related("student__user")
    assignment_list = course.assignment_set.all()
    add_form = AddAssignmentForm()

    return render(request, "portal/teacher_course_detail.html", {
        "course": course,
        "roster": roster,
        "assignment_list": assignment_list,
        "add_form": add_form,
    })


@login_required
@teacher_required
def add_assignment(request, course_id):
    teacher = _get_teacher(request.user)
    course = get_object_or_404(Course, id=course_id, teacher=teacher)

    if request.method == "POST":
        form = AddAssignmentForm(request.POST)
        if form.is_valid():
            Assignment.objects.create(
                course=course,
                title=form.cleaned_data["title"],
                due_text=form.cleaned_data["due_text"],
            )
            messages.success(request, "Assignment created.")

    return redirect("teacher_course_detail", course_id=course.id)


@login_required
@teacher_required
def teacher_submissions(request, assignment_id):
    teacher = _get_teacher(request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id, course__teacher=teacher)

    if request.method == "POST":
        submission_id = request.POST.get("submission_id")
        submission = get_object_or_404(Submission, id=submission_id, assignment=assignment)
        submission.grade = request.POST.get("grade", "")
        submission.feedback = request.POST.get("feedback", "")
        submission.save()
        messages.success(request, f"Graded {submission.student}.")
        return redirect("teacher_submissions", assignment_id=assignment.id)

    # Show every enrolled student, whether or not they've submitted yet
    roster = assignment.course.enrollment_set.select_related("student__user")
    submissions_by_student = {
        s.student_id: s for s in assignment.submissions.all()
    }
    rows = [
        {"enrollment": e, "submission": submissions_by_student.get(e.student_id)}
        for e in roster
    ]

    return render(request, "portal/teacher_submissions.html", {
        "assignment": assignment,
        "rows": rows,
    })
