from typing import Optional
import re

def build_initial_password(email: Optional[str], phone: Optional[str]) -> str:
    """
    Build initial password as:
      first 3 letters of email (lowercased) + '@' + last 3 digits of phone.
    Sanitizes phone to digits only. Falls back to sensible values if inputs short.
    """
    email = (email or "").strip().lower()
    phone = (phone or "").strip()

    # email part: ensure 3 characters (pad with 'x' if shorter)
    email_part = (email[:3] if len(email) >= 3 else email).ljust(3, 'x')

    # phone digits only
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 3:
        phone_part = digits[-3:]
    else:
        # pad on the left with zeros if fewer than 3 digits
        phone_part = digits.rjust(3, '0')

    return f"{email_part}@{phone_part}"
