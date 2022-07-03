from disposable_email.DisposableEmail import DisposableEmail
import pandas as pd
from email.message import EmailMessage
from email.utils import formatdate
import logging

from guerrillamail import GuerrillaMailSession, GuerrillaMailException
from polling import poll, TimeoutException
from IPython.display import clear_output, display, HTML

log = logging.getLogger(__name__)

class GuerillaMail(DisposableEmail):

    def __init__(self, specified_email_addr=None):
        print("setting up GuerrillaMailSession")
        self.email_client_name = "GuerillaMail"
        self.guerillaSession = GuerrillaMailSession(email_address=specified_email_addr) if specified_email_addr else GuerrillaMailSession()  # if email address provided use this for session/inbox

    @property
    def email_address(self) -> str:
        return self.guerillaSession.get_session_state()['email_address']

    @property
    def inbox_size(self):
        return len(self.guerillaSession.get_email_list())

    # def list_inbox(self,) -> list:
    #     raise NotImplementedError(f"list_inbox method not yet implemented for GuerillaMail")

    def list_inbox(self) -> None:
        """ Prints INBOX """
        email_list = self.guerillaSession.get_email_list()
        inbox_list = []
        for email_element in email_list:
            # utils.pretty(email_element.__dict__)
            email = self.guerillaSession.get_email(email_element.guid)
            inbox_list.append(email.__dict__)

        inbox_df = pd.DataFrame(inbox_list)
        inbox_df.index += 1
        # print((inbox_list))
        # display(inbox_df)
        # TODO: create a nice inbox dsummary table
        return inbox_list

    def get_most_recent_email(self) -> EmailMessage:
        if self.inbox_size > 0:
            log.info(f"Inbox has emails -> size: {self.inbox_size}")
            return self.wrap_email(self.guerillaSession.get_email(self.guerillaSession.get_email_list()[0].guid))
        else:
            log.info(f"Inbox is empty")
            return None
        
    def wait_for_next_email(self, timeout=600) -> EmailMessage:
        init_inbox_size = self.inbox_size  # Number of emails at polling start
        try:
            result = poll(
                lambda: self.guerillaSession.get_email_list()[0] if self.inbox_size > init_inbox_size else False,  # return the new first email_element of email_list  ## for testing only; remove 0
                # check_success=is_correct_response,
                # ignore_exceptions=(),
                step=1,
                timeout=timeout)
            # return a properly parsed Email: https://docs.python.org/3/library/email.message.html
            return self.wrap_email(self.guerillaSession.get_email(result.guid)) if result else None

        except TimeoutException as err:
            print(f"Values..\n{(err.values.full())}")
            print(f"Last...\n{err.last}")

    def wrap_email(self, email_GuerillamailEmail) -> EmailMessage:
        msg = EmailMessage()
        msg['Subject'] = email_GuerillamailEmail.subject
        msg['From'] = email_GuerillamailEmail.sender
        msg['To'] = self.email_address
        msg['Date'] = formatdate(email_GuerillamailEmail.datetime.timestamp())
        msg.set_content(email_GuerillamailEmail.body)
        return msg  # returns the Email Object
