from disposable_email.GuerrillaMail import GuerillaMail
from disposable_email.MailSlurp import MailSlurp
import config


def get_email_interface():
    return GuerillaMail()
    # return MailSlurp(config.MAILSLURP_API)

def test_get_current_email_address():
    # initiate email interface
    email_interface = get_email_interface()
    print(type(email_interface))
    email_address = email_interface.email_address
    print(email_address)
    assert email_address is not None

def test_list_inbox():
    # initiate email interface
    email_interface = get_email_interface()
    inbox = email_interface.list_inbox()
    print(inbox)
    assert inbox is not None

# def test_get_most_recent_email():
#     # initiate email interface
#     email_interface = get_email_interface()
#     most_recent_email = email_interface.get_most_recent_email()
#     print(most_recent_email)
#     assert most_recent_email is not None

if __name__ == "__main__":
    test_get_current_email_address()
    pass
