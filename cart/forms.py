from django import forms
from .models import BillingDetail

# You can create a list of country choices dynamically or use a package like django-countries.
COUNTRIES = [
    ("Afghanistan", "Afghanistan"), 
    ("Albania", "Albania"), 
    ("Algeria", "Algeria"),
    # Add more countries as needed...
]

class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingDetail
        fields = ['full_name', 'address', 'city', 'state', 'postal_code', 'country', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set placeholders for fields
        self.fields['full_name'].widget.attrs['placeholder'] = 'Enter name'
        self.fields['address'].widget.attrs['placeholder'] = 'Enter address'
        self.fields['city'].widget.attrs['placeholder'] = 'Enter city'
        self.fields['state'].widget.attrs['placeholder'] = 'Enter state'
        self.fields['postal_code'].widget.attrs['placeholder'] = 'Enter postal code'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter phone number'

        # Replace None with empty strings to prevent "None" from being displayed
        for field in self.fields:
            if self.initial.get(field) is None:
                self.initial[field] = ''
