from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import check_password, make_password


from .models import Teacher


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'email'}),
        label="Email", validators=[
        RegexValidator(
            regex='^[a-z][a-z0-9_\.]{5,32}@[a-z0-9]{2,}(\.[a-z0-9]{2,4}){1,2}$',
            message='Email must be Alphanumeric',
            code='invalid_email'
        ),
    ])
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password', 'name': 'password1'}),
        label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password', 'name': 'password2'}),
        label="Confirm password")
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'username'}),
        label="Username", validators=[
        RegexValidator(
            regex='^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])',
            message='Username must be Alphanumeric',
            code='invalid_username'
        ),
    ])

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Teacher.objects.filter(email=email)
        if qs.exists():
            # err =
            raise forms.ValidationError("email already exists", code='email_error')
        return email

    def clean_password(self):
        pwd1 = self.cleaned_data.get('password1')
        pwd2 = self.cleaned_data.get('password2')
        if pwd1 != pwd2:
            raise forms.ValidationError("Password don't match", code='password_error')
        return pwd1

    class Meta:
        model = Teacher
        fields = ['email', 'username']
        field_order = ['email', 'password1', 'password2']


class AuthenticationForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control fadeIn third zero-raduis', 'type': 'text', 'name': 'email', 'placeholder': 'Email'}),
        label='Email', validators=[
        RegexValidator(
            regex='^[a-z][a-z0-9_\.]{5,32}@[a-z0-9]{2,}(\.[a-z0-9]{2,4}){1,2}$',
            message='Email must be Alphanumeric',
            code='invalid_email'
        ),
    ])
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control fadeIn third zero-raduis', 'type': 'password', 'name': 'password', 'placeholder': 'Password'}),
        label='Password')

    class Meta:
        fields = ['email', 'password']


class RequestForgetPassword(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control fadeIn third zero-raduis', 'type': 'text', 'name': 'email',
               'placeholder': 'Email'}),
        label="Enter your email to reset password.", validators=[
        RegexValidator(
            regex='^[a-z][a-z0-9_\.]{5,32}@[a-z0-9]{2,}(\.[a-z0-9]{2,4}){1,2}$',
            message='Email must be Alphanumeric',
            code='invalid_email'
        ),
    ])

    class Meta:
        fields = ['email']


class ResetNewPassword(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password', 'name': 'password1'}),
        label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password', 'name': 'password2'}),
        label="Confirm password")