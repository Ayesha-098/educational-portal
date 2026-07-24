from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from portal.models import Assignment, Course, Enrollment, ScheduleSlot, Student, Teacher


class Command(BaseCommand):
    help = "Creates demo student + teacher accounts with sample courses, grades, and schedule."

    def handle(self, *args, **options):
        # --- Demo student ---
        user, created = User.objects.get_or_create(
            username="student1",
            defaults={"first_name": "Maya", "last_name": "Torres", "email": "maya.torres@school.edu"},
        )
        if created:
            user.set_password("password123")
            user.save()

        student, _ = Student.objects.get_or_create(
            user=user, defaults={"student_id": "24-08841", "major": "Computer Science"}
        )

        # --- Demo teacher ---
        teacher_user, created = User.objects.get_or_create(
            username="teacher1",
            defaults={"first_name": "Rowan", "last_name": "Osei", "email": "r.osei@school.edu"},
        )
        if created:
            teacher_user.set_password("password123")
            teacher_user.save()

        teacher, _ = Teacher.objects.get_or_create(
            user=teacher_user, defaults={"teacher_id": "T-00042", "department": "Computer Science"}
        )

        # --- Courses (all taught by the demo teacher), enrollments, and schedule ---
        # (code, title, credits, progress%, attendance%, grade, day, time)
        course_data = [
            ("CS 301", "Algorithms", 4, 72, 95, "A-", "Mon", "9:00 AM"),
            ("MATH 214", "Linear Algebra", 3, 58, 85, "B+", "Mon", "11:00 AM"),
            ("PHYS 150", "Modern Physics", 4, 81, 100, "In Progress", "Tue", "11:00 AM"),
            ("ENG 220", "Rhetoric & Argument", 3, 64, 80, "In Progress", "Tue", "1:00 PM"),
            ("ECON 101", "Microeconomics", 2, 90, 90, "A", "Wed", "3:00 PM"),
        ]

        for code, title, credits, progress, attendance_pct, grade, day, time in course_data:
            course, _ = Course.objects.get_or_create(
                code=code, defaults={"title": title, "credits": credits, "teacher": teacher}
            )
            if course.teacher_id is None:
                course.teacher = teacher
                course.save()
            Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={
                    "progress_percent": progress,
                    "attendance_percent": attendance_pct,
                    "grade": grade,
                },
            )
            ScheduleSlot.objects.get_or_create(course=course, day=day, time=time)

        # --- A couple more courses NOT yet joined, so self-enrollment has something to show ---
        extra_courses = [
            ("BIO 110", "Introduction to Biology", 3),
            ("ART 105", "Art History Survey", 2),
        ]
        for code, title, credits in extra_courses:
            Course.objects.get_or_create(code=code, defaults={"title": title, "credits": credits, "teacher": teacher})

        # --- A few upcoming assignments ---
        cs301 = Course.objects.get(code="CS 301")
        math214 = Course.objects.get(code="MATH 214")
        phys150 = Course.objects.get(code="PHYS 150")

        Assignment.objects.get_or_create(course=math214, title="Problem Set 6", due_text="Due tomorrow")
        Assignment.objects.get_or_create(course=phys150, title="Lab Report", due_text="Due in 3 days")
        Assignment.objects.get_or_create(course=cs301, title="Sorting Algorithms Project", due_text="Due in 5 days")

        self.stdout.write(self.style.SUCCESS("Demo data created."))
        self.stdout.write("Student login: 'student1' / 'password123'")
        self.stdout.write("Teacher login: 'teacher1' / 'password123'")
