from django import forms
from django.contrib.auth import forms as admin_forms
{%- if cookiecutter.username_type == "email" %}
from django.forms import EmailField
{%- endif %}
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        {%- if cookiecutter.username_type == "email" %}
        field_classes = {"email": EmailField}
        {%- endif %}


class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)

    class Meta:
        model = User
        {%- if cookiecutter.username_type == "email" %}
        fields = ("email",)
        field_classes = {"email": EmailField}
        {%- else %}
        fields = ("username",)
        {%- endif %}

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("The two password fields didn’t match."))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
