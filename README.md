# Student Portal (Django)

A simple, server-rendered student portal with two roles: **students** and
**teachers**. No JavaScript framework, no API — just Django views and templates.

**Interactive features:**
- **Sign up** as either a Student or a Teacher (pick a role at signup) — this
  creates a `User` plus a matching `Student` or `Teacher` profile.
- **Self-enrollment**: students browse available courses on the Courses page
  and enroll/drop themselves — no admin needed to get started.
- **Submit assignments** — text and/or a file upload. Resubmitting replaces
  your previous submission rather than creating a duplicate.
- **Teachers can**:
  - Create their own courses right from their dashboard
  - See every course they teach, with student and assignment counts
  - Create new assignments for their courses
  - Edit each student's progress %, attendance %, and grade
  - View and grade submitted work (grade + written feedback)

## Project layout

```
studentportal_django/
├── manage.py
├── studentportal/        # project settings & URL root
└── portal/                 # the actual app
    ├── models.py            # Student, Teacher, Course, Enrollment, ScheduleSlot, Assignment, Submission
    ├── forms.py             # signup form (with role choice), assignment/grading forms
    ├── views.py             # one view per page — student views + teacher views
    ├── urls.py
    ├── admin.py             # lets you manage all data at /admin/
    ├── templates/
    │   ├── registration/   # login.html, signup.html
    │   └── portal/          # base.html (student) + teacher_base.html (teacher)
    │                         # + one template per page
    ├── static/portal/
    │   ├── style.css        # all colors as CSS variables — easy to rebrand
    │   └── logo.svg          # crest logo, used in the sidebar + as favicon
    └── management/commands/seed_data.py   # creates demo student + teacher data
```

## Setup

```bash
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data        # creates demo student + teacher accounts
python manage.py createsuperuser  # optional, for /admin/ access

python manage.py runserver
```

Visit **http://127.0.0.1:8000/** and log in with either:

- **Student**: `student1` / `password123`
- **Teacher**: `teacher1` / `password123`

Or click "Create an account" on the login page and pick a role to sign up
fresh. New students start with zero enrolled courses — visit the Courses page
to browse and join whatever's available (the seed data includes two courses
nobody's enrolled in yet, so there's something to try).

## How the two roles fit together

- A `Course` optionally has a `teacher` (set via `/admin/` if not using the
  seed data, or automatically if a teacher creates courses in a future version).
- Students self-enroll via `Enrollment` records they create themselves.
- Teachers only ever see/manage courses where `course.teacher == themselves` —
  enforced in every teacher view (`get_object_or_404(Course, id=..., teacher=teacher)`),
  so one teacher can't edit another's course or grades.

## Customizing for a client

- **Branding**: edit the CSS variables at the top of `portal/static/portal/style.css`,
  swap out `logo.svg`, and update the "Student Portal" / "Teacher Portal" text
  in the two base templates and the login/signup pages.
- **Data**: either edit `seed_data.py`, or once a superuser exists, add/edit
  everything at `/admin/` without touching code — including assigning a
  teacher to a course.
- **New pages/fields**: add a field to a model in `models.py`, run
  `python manage.py makemigrations && python manage.py migrate`, then
  reference it in the matching template.

## Known simplifications (by design, to keep this small)

- Grades are entered manually by the teacher per course (and per assignment
  submission) rather than computed automatically from submissions.
- A course only has one teacher (no co-teaching / TAs).
