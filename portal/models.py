from django.contrib.auth.models import User
from django.db import models


class Student(models.Model):
    """Extra info about a student, linked to Django's built-in User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20)
    major = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Teacher(models.Model):
    """Extra info about a teacher, linked to Django's built-in User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher_id = models.CharField(max_length=20)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Course(models.Model):
    code = models.CharField(max_length=20)       # e.g. "CS 301"
    title = models.CharField(max_length=200)      # e.g. "Algorithms"
    credits = models.IntegerField(default=3)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses"
    )

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    """Links a student to a course, with their progress/grade in it."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_percent = models.IntegerField(default=0)     # 0-100, how much of the course is done
    attendance_percent = models.IntegerField(default=100)  # 0-100, how often they showed up
    grade = models.CharField(max_length=20, default="In Progress")  # e.g. "A-", "In Progress"

    def __str__(self):
        return f"{self.student} in {self.course}"


class ScheduleSlot(models.Model):
    """One class meeting time, e.g. CS 301 on Monday at 9:00 AM."""
    DAY_CHOICES = [
        ("Mon", "Monday"), ("Tue", "Tuesday"), ("Wed", "Wednesday"),
        ("Thu", "Thursday"), ("Fri", "Friday"),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    time = models.CharField(max_length=20)  # kept as text for simplicity, e.g. "9:00 AM"

    def __str__(self):
        return f"{self.course.code} - {self.day} {self.time}"


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    due_text = models.CharField(max_length=50)  # e.g. "Due tomorrow" - simple text, no date logic

    def __str__(self):
        return self.title


class Submission(models.Model):
    """A student's submitted work for one assignment (text and/or a file)."""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submissions")
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="submissions/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now=True)

    # filled in by the teacher, after the fact
    grade = models.CharField(max_length=20, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ("assignment", "student")  # one submission per student per assignment

    def __str__(self):
        return f"{self.student} - {self.assignment}"
