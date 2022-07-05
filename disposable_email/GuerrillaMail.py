from disposable_email.DisposableEmail import DisposableEmail, DisposableEmailException
import pandas as pd
from email.message import EmailMessage
from email.utils import formatdate
import logging
import time

from guerrillamail import GuerrillaMailSession, GuerrillaMailException
from polling import poll, TimeoutException
from IPython.display import clear_output, display, HTML

log = logging.getLogger(__name__)


class GuerrillaMail(DisposableEmail):

    def __init__(self, specified_email_addr=None):
        """
        NB: GuerrillaMailSession does not get attributes (eg. session_id, email address) until one of the get_...() functions are called
        """
        print("setting up GuerrillaMailSession")
        self.email_client_name = "GuerillaMail"
        self.guerrillaSession: GuerrillaMailSession = GuerrillaMailSession(email_address=specified_email_addr) if specified_email_addr else GuerrillaMailSession()  # if email address provided use this for session/inbox

    @property
    def email_address(self) -> str:
        try:
            return self.guerrillaSession.get_session_state()['email_address']
        except GuerrillaMailException as err:
            raise DisposableEmailException(f"Error getting email address: {err}")

    @property
    def inbox_size(self):
        try:
            return len(self.guerrillaSession.get_email_list())
        except GuerrillaMailException as err:
            raise DisposableEmailException(f"Error getting inbox size: {err}")

    def list_inbox(self) -> None:
        try:
            email_list = self.guerrillaSession.get_email_list()
            inbox_list = []
            # iterate through crude email list and create new list having inspected each email.
            for email_element in email_list:
                email = self.guerrillaSession.get_email(email_element.guid)
                inbox_list.append(email.__dict__)
            return inbox_list
        except GuerrillaMailException as err:
            raise DisposableEmailException(f"Error getting inbox: {err}")


    def get_most_recent_email(self) -> EmailMessage:
        try:
            if self.inbox_size > 0:
                log.info(f"Inbox has emails -> size: {self.inbox_size}")
                return self.wrap_email(self.guerrillaSession.get_email(self.guerrillaSession.get_email_list()[0].guid))
            else:
                log.info(f"Inbox is empty")
                return None
        except GuerrillaMailException as err:
            raise DisposableEmailException(f"Error getting most recent email: {err}")
        
    def await_next_email(self, timeout=600) -> EmailMessage:
        """  
        NB: Must be ready to catch the GuerillaMailException 504 timeout and retry until `timeout` seconds have passed.
        Returns a properly parsed Email: https://docs.python.org/3/library/email.message.html
        """
        try:
            init_inbox_size = self.inbox_size  # Number of emails at polling start
            try:
                result = poll(
                    lambda: self.guerrillaSession.get_email_list()[0] if self.inbox_size > init_inbox_size else False,
                    # check_success=is_correct_response,
                    ignore_exceptions=(GuerrillaMailException),  # ignore 504 timeout (from guerillamail timeouts) )errors - this results i retry
                    step=5, # poll every n seconds
                    timeout=timeout
                    )
                return self.wrap_email(self.guerrillaSession.get_email(result.guid)) if result else None
            except TimeoutException:
                log.info(f"TimeoutException: No new emails arrived within the allowed time period ({timeout}).")
                print(f"TimeoutException: No new emails arrived within the allowed time period ({timeout}).")
                return None
        except DisposableEmailException as err: # in fact this can cause to fail off the bat. would be better to try a while loop with some reties?
            log.info(f"DisposableEmailException: {err} raised trying to set init_inbox_size")
            print(f"DisposableEmailException: {err} raised trying to set init_inbox_size")
            raise DisposableEmailException(f"Error awaiting next email: {err}")


    @DisposableEmail.catch_disposable_email_exception
    def test_func(self, timeout=150):
        print(f"Print function from instide --{__name__}--")
        return f"returned value from  --{__name__}--"

    def wrap_email(self, email_GuerillamailEmail) -> EmailMessage:
        msg = EmailMessage()
        msg['Subject'] = email_GuerillamailEmail.subject
        msg['From'] = email_GuerillamailEmail.sender
        msg['To'] = self.email_address
        msg['Date'] = formatdate(email_GuerillamailEmail.datetime.timestamp())
        msg.set_content(email_GuerillamailEmail.body)
        return msg  # returns the Email Object
