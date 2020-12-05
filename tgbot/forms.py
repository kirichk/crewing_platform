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
            'fleet_subscriptions',
            'salary_subscription',
            'contract_subscription',
            'crew_subscription',
            'date_ready',
            'email',
            'subscription'
        )
        widgets = {
            'name': forms.TextInput,
            'phone': forms.TextInput,
            'full_name': forms.TextInput,
            'title_subscriptions': forms.TextInput,
            'fleet_subscriptions': forms.TextInput,
            'salary_subscription': forms.TextInput,
            'contract_subscription': forms.TextInput,
            'crew_subscription': forms.TextInput,
            'date_ready': forms.DateInput,
            'email': forms.TextInput,
            'subscription': forms.CheckboxInput
        }
