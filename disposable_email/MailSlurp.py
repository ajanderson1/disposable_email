import pandas as pd
import logging
from email.message import EmailMessage
from email.utils import formatdate

from guerrillamail import GuerrillaMailSession, GuerrillaMailException
from polling import poll, TimeoutException
import mailslurp_client
from IPython.display import clear_output, display, HTML

from disposable_email.DisposableEmail import DisposableEmail

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)

#  PyTest https://www.mailslurp.com/examples/pytest-read-email/
#  list of all FUnction https://docs.mailslurp.com/ruby/docs/

#  NB: to use first available inbox (ie to conserve API credits) then uncomment line 38


class MailSlurp(DisposableEmail):

    def __init__(self, api_key, specified_email_addr: str = None):
        self.friendly_name = "MailSlurp"

        # set up required MailSlurp Configuration
        self.configuration = mailslurp_client.Configuration()
        self.configuration.api_key['x-api-key'] = api_key

        # create an API client
        self.api_client = mailslurp_client.ApiClient(self.configuration)

        # create controllers
        self.inbox_controller = mailslurp_client.InboxControllerApi(self.api_client)
        self.waitfor_controller = mailslurp_client.WaitForControllerApi(self.api_client)
        self.email_controller = mailslurp_client.EmailControllerApi(self.api_client)

        # uncomment following linke to select teh first available inbox
        # specified_email_addr = self.inbox_controller.get_all_inboxes().content[0].email_address

        # if specific email addres is supplied, attempt to use this.
        if specified_email_addr:
            this_inbox_id = specified_email_addr.split("@")[0]
            try:
                self.inbox = self.inbox_controller.get_inbox(this_inbox_id)
                log.info(f"\nInbox set to \nID: {self.inbox.id}\nemail address: {self.inbox.email_address}")
            except mailslurp_client.ApiException:
                log.error(f"ApiError: likely that the specified email address not valid: {this_inbox_id} is incorrect.\nCreating new inbox...")
                self.inbox = self.inbox_controller.create_inbox(use_domain_pool=True)
                log.info(f"Created inbox: {self.inbox.email_address}.")
        else:  # if no email address supplied then create one (with option for randomising domain [use_domain_pool])
            self.inbox = self.inbox_controller.create_inbox(use_domain_pool=True)
            log.info(f"Created inbox: {self.inbox.email_address}.")

    @property
    def email_address(self) -> str:
        return self.inbox.email_address

    @property
    def inbox_size(self):
        return len(self.guerillaSession.get_email_list())

    def list_inbox(self,) -> list:
        raise NotImplementedError(f"wrap_email method not yet implemented for MailSlurp(because ran out of API credits!!!)")
        inbox_list = []
        # iterate through inbox and wrap each item as email
        return inbox_list

    def send_email(self, recipient: str = None, subject: str = None, body: str = None) -> None:
        self.validate_recipient_email_addr(recipient)
        send_email_options = mailslurp_client.SendEmailOptions()
        send_email_options.to = [recipient]
        send_email_options.subject = "TEST EMAIL - SUBJECT"
        send_email_options.body = "TEST EMAIL - BODY"
        send_email_options.is_html = True
        self.inbox_controller.send_email(self.inbox.id, send_email_options=send_email_options)
        print(f"Sending message to: {recipient} from: {self.inbox.email_address}")

    def wait_for_next_email(self, timeout=100):
        email = self.waitfor_controller.wait_for_latest_email(inbox_id=self.inbox.id, timeout=60000, unread_only=True)
        return self.wrap_email(email) or None

    def get_most_recent_email(self) -> EmailMessage:
        email = self.inbox_controller.get_latest_email_in_inbox(self.inbox.id, timeout_millis=1000)
        return self.wrap_email(email) or None

    def wrap_email(email_mailslurp: mailslurp_client.Email) -> EmailMessage:
        #  raise NotImplementedError(f"wrap_email method not yet implemented for MailSlurp")
        msg = EmailMessage()
        msg['Subject'] = email_mailslurp.subject
        msg['From'] = email_mailslurp._from
        msg['To'] = email_mailslurp._to
        msg['Date'] = formatdate(email_mailslurp.created_at.timestamp())
        msg.add_header
        msg.set_content(email_mailslurp.body)
        return msg  # returns the Email Object
