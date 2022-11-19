from typing import Protocol
from email.message import EmailMessage
import re
from functools import wraps
import traceback

import logging
log = logging.getLogger(__name__)

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

    email_client_friendly_name: str = None
    api_key: str = None  # client-specific API key
    specified_email_addr: str = None  # to check an assigned email address
    password: str = None  # to check an assigned email address

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

    # def inbox_as_html(inbox: list) -> None:
    #     """
    #     write out inbox as html table
    #     """
    #     inbox_df = pd.DataFrame(inbox)
    #     inbox_df.index += 1
    #     return inbox_df.to_html('inbox.html')

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
    def validate_email_addr(email_addr):
        """ Ensure that emaill address conforms to valid structure and return if True """

        EMAIL_REGEX = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.I)

        log.debug(f"Validationg: {email_addr}")        
        if(re.fullmatch(EMAIL_REGEX, email_addr)):
            return email_addr
        else:
            raise ValueError("Invalid Email...")
    
    @staticmethod
    def extract_pre(email_body: str) -> str:
        PRE_TAG_REGEX = re.compile(r'<pre>(.*?)<\/pre>', re.I)
        return re.search(PRE_TAG_REGEX, email_body)

    
    # create a decorator to catch DisposableEmailException and return a friendly message
    def retry_upon_error(retries = 1):
        """
        Decorator to catch DisposableEmailException for *any* reason and attempt retry until user specified timeout.        
        This is to allow for failures/timeouts of any kind to be handled in a consistent manner.
        
        params: retries - number of times to retry the function.
        """
        def decorate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                attempt = 0
                while attempt < retries:
                    attempt += 1
                    log.debug(f"This is Attempt {attempt} of {retries} ({func.__name__})")
                    try:
                        return func(*args, **kwargs)
                    except Exception as err:  #  may be raised for any reason, regardless...
                        will_retry = True if attempt < retries else False
                        log.debug(f"Exception raised: {err}\nWill Retry?: {will_retry}")
                log.debug(f"Function ({__name__}) raised exception: {traceback}.")
                raise DisposableEmailException(f"Completed {attempt} of {retries} attempts.")                                                
            return wrapper
        return decorate
   
   
if __name__ == '__main__':
    import sys
    print(sys.path)  # .append('../parentdirectory')
