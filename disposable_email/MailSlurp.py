from random import randint
import logging
from email.message import EmailMessage
from email.utils import formatdate

from guerrillamail import GuerrillaMailSession, GuerrillaMailException
from polling2 import poll, TimeoutException
import mailslurp_client
from IPython.display import clear_output, display, HTML

from disposable_email.DisposableEmail import DisposableEmail, DisposableEmailException

log = logging.getLogger(__name__)
#  PyTest https://www.mailslurp.com/examples/pytest-read-email/
#  list of all FUnction https://docs.mailslurp.com/ruby/docs/

#  NB: to use first available inbox (ie to conserve API credits) then uncomment line 38

# NOTES:
# Trying to extended the funcitonality here to include the following:
# 1. Use existing inbox (ie. do not create new inbox) at random - this will conserve credits

class MailSlurp(DisposableEmail):

    def __init__(self, api_key, specified_email_addr: str = None, use_existing_inbox = False, use_first = False, use_domain_pool = False):
        """
        
        :param api_key: client-specific API key
        :param specified_email_addr: to check an assigned email address
        :param use_existing_inbox: use existing inbox (ie. attempt to use a current inbox)
        :param use_first: use first available inbox (ie. if False, will select at random)
        :param use_domain_pool: use domain pool (ie. use differnet domains)

        """
        
        self.email_client_friendly_name = "MailSlurp"

        if use_existing_inbox and specified_email_addr:
            log.warning(f"You have specified a specific email address: {specified_email_addr} but have set use_existing_inbox to True. Will attempt to use specified email, otherwise create inbox.")

        # set up required MailSlurp Configuration
        self.configuration = mailslurp_client.Configuration()
        self.configuration.api_key['x-api-key'] = api_key

        # create an API client
        self.api_client = mailslurp_client.ApiClient(self.configuration)

        # create controllers
        self.inbox_controller = mailslurp_client.InboxControllerApi(self.api_client)
        self.waitfor_controller = mailslurp_client.WaitForControllerApi(self.api_client)
        self.email_controller = mailslurp_client.EmailControllerApi(self.api_client)

        # if specific email addres is supplied, attempt to use this.
        if specified_email_addr and DisposableEmail.validate_email_addr(specified_email_addr):
            this_inbox_id = specified_email_addr.lstrip().split("@")[0]
            try:
                self.inbox = self.inbox_controller.get_inbox(this_inbox_id)
                log.info(f"\nInbox set to \nID: {self.inbox.id}\nemail address: {self.inbox.email_address}")
            except mailslurp_client.ApiException:
                log.warning(f"ApiError: likely that the specified email address not valid: {this_inbox} is incorrect.\nCreating new inbox...")
                self.inbox = self.inbox_controller.create_inbox(use_domain_pool=use_domain_pool)
                log.info(f"Created inbox: {self.inbox.email_address}.")
        # else if no specific email address is supplied and use_existing_inbox is True, attempt to use existing inbox.
        elif use_existing_inbox:
            list_of_avail_inboxes: list[mailslurp_client.models.inbox_preview.InboxPreview] = self.inbox_controller.get_all_inboxes().content
            if  len(list_of_avail_inboxes) > 0:
                print(f"There are {len(list_of_avail_inboxes)} inboxes available.\n")
                this_inbox = list_of_avail_inboxes[0] if use_first else list_of_avail_inboxes[randint(0, len(list_of_avail_inboxes) - 1)] 
                self.inbox = self.inbox_controller.get_inbox(this_inbox.id)
                log.info(f"\nthisInbox set to \nID: {self.inbox.id}\nemail address: {self.inbox.email_address}")
            else:
                log.warning(f"No inboxes available. Creating new inbox...")
                self.inbox = self.inbox_controller.create_inbox(use_domain_pool=use_domain_pool)
                log.info(f"Created inbox: {self.inbox.email_address}.")
        # Otherwise simply create inbox
        else:
            self.inbox = self.inbox_controller.create_inbox(use_domain_pool=use_domain_pool)
            log.info(f"Created inbox: {self.inbox.email_address}.")

    @property
    def email_address(self) -> str:
        return self.inbox.email_address

    @property
    def inbox_size(self):
        return self.inbox_controller.get_inbox_email_count(self.inbox.id) if self.inbox_controller.get_inbox_email_count > 0 else 0

    @property
    def inbox_size(self):
        inbox_size = self.inbox_controller.get_inbox_email_count(self.inbox.id)
        return inbox_size.total_elements if inbox_size else 0


    def list_inbox(self,) -> list:
        all_emails = self.inbox_controller.get_emails(self.inbox.id)
        # print((all_emails[0]).__dict__)  # NB: this retutned type mailslup_client.emailPreview
        for email in all_emails:
            print(f"{email.id} // {email.subject} // {email._from}")
            return all_emails

    def send_email(self, recipient: str = None, subject: str = None, body: str = None) -> None:
        self.validate_recipient_email_addr(recipient)
        send_email_options = mailslurp_client.SendEmailOptions()
        send_email_options.to = [recipient]
        send_email_options.subject = "TEST EMAIL - SUBJECT"
        send_email_options.body = "TEST EMAIL - BODY"
        send_email_options.is_html = True
        self.inbox_controller.send_email(self.inbox.id, send_email_options=send_email_options)
        print(f"Sending message to: {recipient} from: {self.inbox.email_address}")

    @DisposableEmail.retry_upon_error
    def await_next_email(self, timeout=10):
        try:
            email = self.waitfor_controller.wait_for_latest_email(inbox_id=self.inbox.id, timeout=timeout*1000, unread_only=True)
            return self.wrap_email(email)
        except mailslurp_client.ApiException as err:
            log.warning(f"No new emails arrived withing {timeout} seconds.")
            return None

    def get_most_recent_email(self) -> EmailMessage:
        try:
            email = self.email_controller.get_latest_email_in_inbox1(self.inbox.id)
            return self.wrap_email(email) or None
        except mailslurp_client.ApiException as err:
            log.warning(f"There are no emails in this inbox.")
            return None

    @staticmethod
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



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    MAILSLURP_API = "83fbe003801611e35ebd9865e627163fd3cc23231aac0b54cffd9e4bef20e992"
    log.info(f"how many log handlers are there: {len(logging.root.handlers)}")
    test = MailSlurp(api_key=MAILSLURP_API, use_existing_inbox=True, use_first=True)
    print(f"Testing inbox size")
    print(test.get_most_recent_email())
    print(test.list_inbox())  

    print(f"\n\nNow watigin on next eimal")
    test.await_next_email(10) # Will attempt 3x Nsecs to get email, and will raise exception if no email arrives within 50s. Meanwhile running is blocked.
