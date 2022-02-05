import DisposableEmail
import pandas as pd
from typing import Protocol
from email.message import EmailMessage
from guerrillamail import GuerrillaMailSession, GuerrillaMailException
from polling import poll, TimeoutException
import mailslurp_client
from IPython.display import clear_output, display, HTML
from ..config import MAILSLURP_API


class MailSlurp(DisposableEmail):

    # TODO: Ran out of API credits so had to stop play

    def __init__(self, api_key):
        self.email_client_name = "MailSlurp"
        self.configuration = mailslurp_client.Configuration()
        self.configuration.api_key['x-api-key'] = api_key
        # create an API client
        self.api_client = mailslurp_client.ApiClient(self.configuration)
        # create an API instance
        self.api_instance = mailslurp_client.InboxControllerApi(self.api_client)
        self.inbox = self.api_instance.create_inbox()

    @property
    def email_address(self) -> str:
        return self.api_instance.get_inbox_count()

    @property
    def inbox_size(self):
        return len(self.guerillaSession.get_email_list())

    # NB: there exists a function (with this name) in the Mailslurp package. See: https://www.mailslurp.com/docs/ruby/docs/InboxControllerApi/
    def send_test_email(self, recipient_email_addr: str) -> None:
        self.validate_recipient_email_addr(recipient_email_addr)
        send_email_options = mailslurp_client.SendEmailOptions()
        send_email_options.to = [recipient_email_addr]
        send_email_options.subject = "TEST EMAIL - SUBJECT"
        send_email_options.body = "TEST EMAIL - BODY"
        send_email_options.is_html = True
        self.api_instance.send_email(self.inbox.id, send_email_options=send_email_options)
        print(f"Sending message to: {recipient_email_addr} from: {self.inbox.email_address}")

    def wait_for_next_email(self, timeout=100):
        waitfor_controller = mailslurp_client.WaitForControllerApi(self.api_client)
        email = waitfor_controller.wait_for_latest_email(inbox_id=self.inbox.id, timeout=60000, unread_only=True)
        return self.create_Email_instance(email) or None

    def create_Email_instance(self, this_email) -> EmailMessage:
        raise NotImplementedError(f"create_Email_instance method not yet implemented for MailSlurp(because ran out of API credits!!!)")
        return msg  # returns the Email Object



def main(disposable_email: DisposableEmail) -> None:

    my_disposable_email = disposable_email(MAILSLURP_API)
    print(f"Testing email address: {my_disposable_email.email_address}")

    # testing waiting on email
    print('waiting on email...')
    print(my_disposable_email.wait_for_next_email())

    # # send a test email to test 'wait for email'
    # send_test_message = MailSlurp(API)
    # send_test_message.send_test_email(my_disposable_email.email_address)


if __name__ == '__main__':
    print(help(DisposableEmail))

    # main(GuerillaMail)
    # main(MailSlurp)
