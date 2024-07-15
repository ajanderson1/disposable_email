import pytest
from disposable_email.DisposableEmail import DisposableEmail, DisposableEmailException

def test_disposable_email_protocol():
    with pytest.raises(TypeError):
        DisposableEmail()

def test_disposable_email_exception():
    with pytest.raises(DisposableEmailException):
        raise DisposableEmailException("This is a test exception")