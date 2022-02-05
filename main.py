from typing import Protocol
from email.message import EmailMessage
import re


class DisposableEmail(Protocol):
    """
    Initiate a session/inbox - treated as same thing
    as in most case only require single inbox.
    Where multiple inboxes are required, create separate instances
    """
    email_client_name: str = None
    api_key: str = None  # client-specific API key
    specified_email_addr: str = None  # to check an assigned email address
    password: str = None  # to check an assigned email address

    @property
    def email_address(self) -> str:
        """ Email address of created disposable email session """
        ...

    @property
    def inbox_size(self):
        """ Get number of items in inbox """
        ...

    def wait_for_next_email(self, timeout=100) -> str:
        """
        Poll next email to arrive and return it.
        """
        ...

    def create_Email_instance(self, this_email) -> EmailMessage:
        """
        wrap up the email object used by this email provider (GuerillaMail/MailSlurp/etc)
        as the Python standard email Object (see: https://docs.python.org/3/library/email.html)
        """

    @staticmethod
    def validate_recipient_email_addr(recipient_email_addr):
        print(f"validationg: {recipient_email_addr}")
        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+", re.I)
        if not EMAIL_REGEX.match(recipient_email_addr):
            raise ValueError("Invalid Email...")
        if recipient_email_addr.split('@')[-1] in ['gmail.com', 'googlemail.com', 'yahoo.com']:  # ....@gmail.com etc not valid for some disposable email clients
            raise ValueError("MailSlurp cannot send emails to this domain...")

    @staticmethod
    def extract_pre(email_body: str) -> str:
        PRE_TAG_REGEX = re.compile(r'<pre>(.*?)<\/pre>', re.I)
        return re.search(PRE_TAG_REGEX, email_body)
