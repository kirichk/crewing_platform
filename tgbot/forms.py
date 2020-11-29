from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = (
            'external_id',
            'name',
            'phone',
            'full_name',
            'title_subscriptions',
            'salary_range'
        )
        widgets = {
            'name': forms.TextInput,
            'phone': forms.TextInput,
            'full_name': forms.TextInput,
            'title_subscriptions': forms.TextInput,
            'salary_range': forms.TextInput,
        }
