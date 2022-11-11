from disposable_email.DisposableEmail import DisposableEmail, DisposableEmailException
import pandas as pd
from email.message import EmailMessage
from email.utils import formatdate
from rich.console import Console
from guerrillamail import GuerrillaMailSession, GuerrillaMailException
from polling2 import poll, TimeoutException

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class GuerrillaMail(DisposableEmail):

    def __init__(self, specified_email_addr=None):
        """
        NB: GuerrillaMailSession does not get attributes (eg. session_id, email address) until one of the get_...() functions are called

        """
        log.info(f"Testing logging - {__name__}")
        self.email_client_friendly_name = "GuerillaMail"
        if specified_email_addr:
            log.warning(f"NB: User has provided Specified email address.  Please note that only the username part (before the @) will be used alongwith the domain '@guerrillmailablock.com'.\
                        \nIf multiple '@' symbols are present, everything before first one will be used\
                        \nAny unallowed chars (includeing spaces) are ignored.")
        self.guerrillaSession: GuerrillaMailSession = GuerrillaMailSession(
            email_address=specified_email_addr) if specified_email_addr else GuerrillaMailSession()  # if email address provided use this for session/inbox
        self.email_address = self.get_email_address()
        log.info(f"email_address: {self.guerrillaSession.email_address}")

    @DisposableEmail.retry_upon_error(3)
    def get_email_address(self, *args, **kwargs) -> str:
        log.debug("Attempting to return email address")
        return self.guerrillaSession.get_session_state()['email_address']

    @property
    @DisposableEmail.retry_upon_error(3)
    def inbox_size(self, *args, **kwargs) -> int:
        return len(self.guerrillaSession.get_email_list())

    @DisposableEmail.retry_upon_error(3)
    def list_inbox(self, *args, **kwargs) -> list:
        email_list = self.guerrillaSession.get_email_list()
        inbox_list = []
        # iterate through crude email list and create new list having inspected each email.
        for email_element in email_list:
            email = self.guerrillaSession.get_email(email_element.guid)
            inbox_list.append(email.__dict__)
        return inbox_list

    @DisposableEmail.retry_upon_error(3)
    def get_most_recent_email(self, *args, **kwargs) -> EmailMessage:
        if self.inbox_size > 0:
            log.info(f"Inbox has emails -> size: {self.inbox_size}")
            return self.wrap_email(self.guerrillaSession.get_email(self.guerrillaSession.get_email_list()[0].guid))
        else:
            log.info(f"Inbox is empty")
            return None

    @DisposableEmail.retry_upon_error(3)
    def await_next_email(self, timeout=60, *args, **kwargs) -> EmailMessage:
        init_inbox_size = self.inbox_size  # Number of emails at polling start
        log.debug(f"init_inbox_size: {init_inbox_size}")
        try:
            console = Console()
            with console.status(f"[bold green]Awaiting next email({self.email_address})...") as status:
                result = poll(
                    lambda: self.guerrillaSession.get_email_list(
                    )[0] if self.inbox_size > init_inbox_size else False,
                    # check_success=is_correct_response,
                    # ignore 504 timeout (from guerillamail timeouts) )errors - this results i retry
                    ignore_exceptions=(GuerrillaMailException),
                    step=5,  # poll every n seconds  # potentially increased by how quickly we receive back inbox size request
                    timeout=timeout
                )
                return self.wrap_email(self.guerrillaSession.get_email(result.guid)) if result else None
        except TimeoutException:
            log.info(
                f"TimeoutException: No new emails arrived within the allowed time period ({timeout}s).")
            # or return None, but this will only ever run once regadless of decoartar.
            raise DisposableEmailException(f"Error awaiting next email")

    @DisposableEmail.retry_upon_error(3)
    def test_func(self, timeout):
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    test = GuerrillaMail('qfxfsveb@guerrillamailblock.com')
    print(f"Inbox Size: {test.inbox_size}")
    print(test.await_next_email())
    # test.await_next_email(50) # Will attempt 3x Nsecs to get email, and will raise exception if no email arrives within 50s. Meanwhile running is blocked.
