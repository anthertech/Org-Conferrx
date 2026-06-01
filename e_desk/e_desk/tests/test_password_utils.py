import pytest
from e_desk.e_desk.utils.password_utils import build_initial_password

def test_basic_email_phone():
    assert build_initial_password('Alice@example.com', '+91-9876543210') == 'ali@210'

def test_short_email_and_phone():
    # email shorter than 3 -> padded with x, phone shorter than 3 -> left-padded with zeros
    assert build_initial_password('ab', '9') == 'abx@009'

def test_non_digit_phone():
    assert build_initial_password('bob@test.com', '(12)34') == 'bob@234'
