from disposable_email import GuerrillaMail

import logging
log = logging.getLogger(__name__)

# def get_email_interface():
#     return GuerrillaMail()
#     # return MailSlurp(config.MAILSLURP_API)

# def test_get_current_email_address():
#     # initiate email interface
#     email_interface = get_email_interface()
#     print(type(email_interface))
#     email_address = email_interface.email_address
#     print(email_address)
#     assert email_address is not None


# def test_inbox_size():
#     # initiate email interface
#     email_interface = get_email_interface()
#     print(type(email_interface))
#     inbox_size = email_interface.inbox_size
#     assert inbox_size > 0


# def test_list_inbox():
#     # initiate email interface
#     email_interface = get_email_interface()
#     inbox = email_interface.list_inbox()
#     print(inbox)
#     assert inbox is not None

# def test_get_most_recent_email():
#     # initiate email interface
#     email_interface = get_email_interface()
#     most_recent_email = email_interface.get_most_recent_email()
#     print(most_recent_email)
#     assert most_recent_email is not None

# def test_await_next_email():
#     # initiate email interface
#     email_interface = get_email_interface()
#     next_email = email_interface.await_next_email(timeout=120)
#     # need to send any email here.
#     print(next_email)
#     assert next_email is not None
