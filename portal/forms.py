from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    ROLE_CHOICES = [("student", "Student"), ("teacher", "Teacher")]

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, initial="student")
    email = forms.EmailField(required=True)
    major_or_department = forms.CharField(
        required=False, help_text="Your major (students) or department (teachers) - optional"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class AddAssignmentForm(forms.Form):
    title = forms.CharField(max_length=200)
    due_text = forms.CharField(max_length=50, help_text='e.g. "Due Friday"')


class CreateCourseForm(forms.Form):
    code = forms.CharField(max_length=20, help_text='e.g. "CS 401"')
    title = forms.CharField(max_length=200, help_text='e.g. "Distributed Systems"')
    credits = forms.IntegerField(min_value=1, max_value=10, initial=3)


class GradeSubmissionForm(forms.Form):
    grade = forms.CharField(max_length=20, required=False)
    feedback = forms.CharField(widget=forms.Textarea, required=False)
