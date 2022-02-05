import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from disposable_email.DisposableEmail import DisposableEmail
from disposable_email.GuerillaMail import GuerillaMail
from disposable_email.MailSlurp import MailSlurp

from config import MAILSLURP_API


if __name__ == '__main__':
    # print(help(DisposableEmail))

    API = MAILSLURP_API

    my_disposable_email = MailSlurp(API)
    print(f"Testing email address: {my_disposable_email.email_address}")
    my_disposable_email.send_email(my_disposable_email.email_address)


    # testing waiting on email
    print('waiting on email...')
    print(my_disposable_email.wait_for_next_email())

    # # send a test email to test 'wait for emsail'