import time
from typing import Protocol
from email.message import EmailMessage
import re
import pandas as pd

# create custom exception
class DisposableEmailException(Exception):
    """ Specialized exception for DisposableEmail Protocol """
    pass



class DisposableEmail(Protocol):
    """
    Initiate a session/inbox - treated as same thing
    as in most case only require single inbox.
    Where multiple inboxes are required, create separate instances
    """

    friendly_name: str = None
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

    def list_inbox(self):
        """
        returns inbox as a list of Emails:Email
        """
        ...

    def send_email(self, recipient: str = None, subject: str = None, body: str = None) -> None:
        """
        Send email
        """
        ...

    def get_most_recent_email(self) -> EmailMessage:
        """
        Return most recent email.
        """
        ...

    def await_next_email(self, timeout=100) -> EmailMessage:
        """
        Poll next email to arrive and return it.
        """
        ...

    def wrap_email(self, this_email) -> EmailMessage:
        """
        wrap up the email object used by this email provider (GuerillaMail/MailSlurp/etc)
        as the Python standard email Object (see: https://docs.python.org/3/library/email.html)
        """

    def inbox_as_html(inbox: list) -> None:
        """
        write out inbox as html table
        """

        inbox_df = pd.DataFrame(inbox)
        inbox_df.index += 1
        return inbox_df.to_html('inbox.html')

    @staticmethod
    def validate_recipient_email_addr(recipient_email_addr):
        print(f"validationg: {recipient_email_addr}")
        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+", re.I)
        if not EMAIL_REGEX.match(recipient_email_addr):
            raise ValueError("Invalid Email...")
        if recipient_email_addr.split('@')[-1] in [
                                'gmail.com', 
                                'googlemail.com', 
                                'yahoo.com'
                                ]:  # ....@gmail.com etc not valid for some disposable email clients
            print(f"WARNING: Some clients cannot send emails to this domain...")

    @staticmethod
    def extract_pre(email_body: str) -> str:
        PRE_TAG_REGEX = re.compile(r'<pre>(.*?)<\/pre>', re.I)
        return re.search(PRE_TAG_REGEX, email_body)

    
    # create a decorator to catch DisposableEmailException and return a friendly message
    def catch_disposable_email_exception(func):
        func_starttime = time.time()
        print(f"function: {func.__name__}, started at: {func_starttime}")
        print("PRINGING SOMETRHING!!!!")
        def wrapper(*args, **kwargs):
            timeout=kwargs.get('timeout') or 100
            print(f"Timeout is set to: {timeout}")
            print(f"so  func_starttime + timeout = { func_starttime + timeout}")
            print(f"...and time now is: {time.time()}")
            while time.time()< func_starttime + timeout:
                print(f"ok  func_starttime + timeout is less than time.time()")
                try:
                    func(*args, **kwargs)
                except DisposableEmailException as e:
                    print(f"Caight the timeout exception: {e}\nWa")
                    time.sleep(1) 
        return wrapper


if __name__ == '__main__':
    import sys
    print(sys.path)  # .append('../parentdirectory')
