from django import forms
from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm


class RoomForm(ModelForm):
    # Meta class is an inner class in Django models. Which contain Meta options(metadata) that are used to change the behavior of your model fields like changing order options, whether the model is abstract or not, singular and plural versions of the name etc
    class Meta:
        # The model you wish to create a form for, in this case we wish to create form for Room.
        model = Room
        # It creates the necessary fields e.g. dropdown list for host/topic, CharField for name, TextField for description etc.
        fields = '__all__'
        exclude = ['host', 'participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']
        