import DisposableEmail
import pandas as pd
from guerrillamail import GuerrillaMailSession, GuerrillaMailException
from polling import poll, TimeoutException
from IPython.display import clear_output, display, HTML

class GuerillaMail(DisposableEmail):

    def __init__(self, specified_email_addr=None):
        self.email_client_name = "GuerillaMail"
        self.guerillaSession = GuerrillaMailSession(email_address=specified_email_addr) if specified_email_addr else GuerrillaMailSession()  # if email address provided use this for session/inbox
        self.email_address = specified_email_addr

    @property
    def email_address(self) -> str:
        return self.guerillaSession.get_session_state()['email_address']

    @property
    def inbox_size(self):
        return len(self.guerillaSession.get_email_list())

    # TODO: returning any email ->  make new methods for return next new mail, return all, return matching email.

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
            return self.create_Email_instance(self.guerillaSession.get_email(result.guid)) if result else False

        except TimeoutException as err:
            print(f"Values..\n{(err.values.full())}")
            print(f"Last...\n{err.last}")

    def create_Email_instance(self, this_email) -> EmailMessage:
        msg = EmailMessage()
        msg.add_header("From", this_email.sender)
        msg.add_header("To", self.email_address)
        msg.add_header("Subject", this_email.subject)
        msg.add_header("Date", this_email.datetime)
        msg.preamble = print(DisposableEmail.extract_pre(this_email.body))
        msg.set_content = this_email.body
        # msg['guid'] = this_email.guid
        # msg['read'] = this_email.read
        return msg  # returns the Email Object

    #  ADDIONTAL email client-specific functions

    @staticmethod
    def display_inbox(guerillaSession: GuerrillaMailSession) -> None:
        """ Prints INBOX """
        email_list = guerillaSession.get_email_list()
        inbox_list = []
        for email_element in email_list:
            # utils.pretty(email_element.__dict__)
            email = guerillaSession.get_email(email_element.guid)
            inbox_list.append(email.__dict__)

        inbox_df = pd.DataFrame(inbox_list)
        inbox_df.index += 1
        display(inbox_df)
