from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Reset, Div, Field, Button
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    username = forms.CharField(
        max_length=200,
        required=True,
        help_text=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
    )

    class Meta:
        model = User
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'  # get or post
        self.helper.attrs = {
            'novalidate': ''
        }
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-12'),
                Column('password', css_class='col-12'),
            ),
            Div(
                Reset('reset', 'Cancel', css_class='btn-danger'),
                Submit('submit', 'Login', css_class='btn-dark'),
                css_class="modal-footer px-0",
            )
        )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput(), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")
    username = forms.CharField(
        max_length=200,
        required=True,
        help_text=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
    )

    class Meta:
        model = User
        fields = ('email', 'password1', "password2", 'first_name', 'last_name', 'username')

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()  # running sql in database to store data
        return user


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'  # get or post
        self.helper.attrs = {
            'novalidate': ''
        }
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-12 col-sm-6'),
                Column('last_name', css_class='col-12 col-sm-6'),
                Column('username', css_class='col-12 col-sm-6'),
                Column('email', css_class='col-12 col-sm-6'),
                Column('password1', css_class='col-12 col-sm-6'),
                Column('password2', css_class='col-12 col-sm-6'),
            ),
            Div(
                Reset('reset', 'Cancel', css_class='btn-danger'),
                Submit('submit', 'Register', css_class='btn-dark'),
                css_class="modal-footer px-0",
            )
        )
