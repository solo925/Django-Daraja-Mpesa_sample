def standardize_phone_number(phone_number):
    """
    Standardizes phone number to the format 2547XXXXXXXX.
    """
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]
    if phone_number.startswith("0"):
        phone_number = "254" + phone_number[1:]
    return phone_number
