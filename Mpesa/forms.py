from django import forms
from .models import User

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number']

class PaymentForm(forms.Form):
    phone_number = forms.CharField(max_length=15)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
