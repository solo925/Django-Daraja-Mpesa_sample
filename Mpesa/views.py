from django.shortcuts import render,redirect
from .forms import RegistrationForm, PaymentForm
from .models import User
import requests
from django.conf import settings
from django.http import JsonResponse

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payment')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            amount = form.cleaned_data['amount']
            response = initiate_mpesa_payment(phone_number, amount)
            return JsonResponse(response)
    else:
        user = User.objects.latest('id')
        form = PaymentForm(initial={'phone_number': user.phone_number})
    return render(request, 'payment.html', {'form': form})

def initiate_mpesa_payment(phone_number, amount):
    consumer_key = settings.CONSUMER_KEY
    consumer_secret = settings.CONSUMER_SECRET
    shortcode = settings.SHORTCODE
    lipa_na_mpesa_online_shortcode = settings.LIPA_NA_MPESA_ONLINE_SHORTCODE
    lipa_na_mpesa_online_passkey = settings.LIPA_NA_MPESA_ONLINE_PASSKEY

    access_token = get_mpesa_access_token(consumer_key, consumer_secret)
    if not access_token:
        return {"error": "Failed to get access token"}

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    custom_account_reference="solo925"
    payload = {
        "BusinessShortCode": lipa_na_mpesa_online_shortcode,
        "Password": generate_password(lipa_na_mpesa_online_shortcode, lipa_na_mpesa_online_passkey),
        "Timestamp": get_timestamp(),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://example.com/callback",
        # "AccountReference": "Solo925",
        # "TransactionDesc": "Payment to Solo925 Agencies"
        "AccountReference": custom_account_reference,  # Custom reference
        "TransactionDesc": f"Payment for {amount} Ksh for your order",
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

def get_mpesa_access_token(consumer_key, consumer_secret):
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_url, auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def generate_password(shortcode, passkey):
    import base64
    import datetime
    timestamp = get_timestamp()
    data_to_encode = shortcode + passkey + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode())
    return encoded_string.decode('utf-8')

def get_timestamp():
    import datetime
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')
