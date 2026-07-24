from django.contrib import admin

from .models import Student, Teacher, Course, Enrollment, ScheduleSlot, Assignment, Submission

# Registering these means you can add/edit all portal data at /admin/
# without writing any extra code.
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(ScheduleSlot)
admin.site.register(Assignment)
admin.site.register(Submission)
