import re
import unittest

import os
import sys

from disposable_email.DisposableEmail import DisposableEmail
from disposable_email.GuerillaMail import GuerillaMail
from disposable_email.MailSlurp import MailSlurp

from config import MAILSLURP_API


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestGuerillaMail(unittest.TestCase):
    def setUp(self) -> None:
        test_email_addr = "vwmnvbhw@guerrillamailblock.com"
        self.my_disposable_email = GuerillaMail(test_email_addr)
        
    def test_list_inbox(self):
        """
        Test list_inbox returns inbox
        """
        pass
    
    def test_send_email(self):
        """
        Test send_email successfully sends an email.
        """
        recipient: str = "emial@asfiojc.com"
        subject: str = "test subj" 
        body: str = "tetbody"
        self.my_disposable_email.send_email(recipient, subject, body)




if __name__ == '__main__':
    print('sdfsdfs')
    print (MAILSLURP_API)
    # # print(help(DisposableEmail))

    # API = MAILSLURP_API
    # # my_disposable_email = MailSlurp(api_key=API, specified_email_addr="aadaf10e-800e-4408-b982-685b13d6ca7a@mailslurp.com")
    # test_email_addr = "vwmnvbhw@guerrillamailblock.com"
    # my_disposable_email = GuerillaMail(test_email_addr)
    
    
    # print(f"Testing email address: {my_disposable_email.email_address}")
    # print(my_disposable_email.get_most_recent_email())
    # # print(my_disposable_email.wait_for_next_email())
