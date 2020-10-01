from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, PasswordChangeForm
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from .models import Teacher
from django.contrib.auth import get_user_model


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
        attrs={'class': 'form-control fadeIn third zero-raduis psw-field', 'type': 'password', 'name': 'password', 'placeholder': 'Password'}),
        label='Password')

    class Meta:
        fields = ['email', 'password']


class RequestForgetPassword(PasswordResetForm):
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


class ResetNewPassword(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password', 'name': 'password1'}),
        label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password', 'name': 'password2'}),
        label="Confirm password")

    def check_pass(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError("Password don't match!")

    class Meta:
        model = get_user_model()
        fields = ['password1', 'password2']


class ChangePasswordForm(PasswordChangeForm):
    pass