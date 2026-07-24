from django.urls import path

from . import views

urlpatterns = [
    # --- Auth ---
    path("accounts/signup/", views.signup, name="signup"),
    path("post-login/", views.post_login, name="post_login"),

    # --- Student pages ---
    path("", views.dashboard, name="dashboard"),
    path("courses/", views.courses, name="courses"),
    path("courses/<int:course_id>/enroll/", views.enroll_course, name="enroll_course"),
    path("courses/drop/<int:enrollment_id>/", views.drop_course, name="drop_course"),
    path("grades/", views.grades, name="grades"),
    path("attendance/", views.attendance, name="attendance"),
    path("schedule/", views.schedule, name="schedule"),
    path("assignments/", views.assignments, name="assignments"),
    path("assignments/<int:assignment_id>/submit/", views.submit_assignment, name="submit_assignment"),
    path("profile/", views.profile, name="profile"),

    # --- Teacher pages ---
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher/courses/create/", views.create_course, name="create_course"),
    path("teacher/courses/<int:course_id>/", views.teacher_course_detail, name="teacher_course_detail"),
    path("teacher/courses/<int:course_id>/add-assignment/", views.add_assignment, name="add_assignment"),
    path("teacher/assignments/<int:assignment_id>/submissions/", views.teacher_submissions, name="teacher_submissions"),
]
