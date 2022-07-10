import asyncio
from async_timeout import timeout
from guerrillamail import GuerrillaMailSession, GuerrillaMailException
from disposable_email.DisposableEmail import DisposableEmailException, DisposableEmail

import logging
import time
from functools import wraps

from guerrillamail import GuerrillaMailSession, GuerrillaMailException
from polling import poll, TimeoutException
from IPython.display import clear_output, display, HTML

log = logging.getLogger(__name__)

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
log.addHandler(c_handler)
log.setLevel(logging.DEBUG)


"""
NOTES:

This was a good explore in async.

@as_async_to_thread - does nothing more than wrap a blocking function into an (awaitable task) thread.
@as_asyncio_wait_for - basicaly then call a wait on this task.  NB: even when time limit (which is caught in this example)
reaches the end, the task (thread) will still continue in the background and be therefore may cause unxepected behaviours
@retry_upon_error - was an effort at retrying the task over and over until it worked.  However, it not super useful

Conculsion, in the end couldnt really map this back to use successfully as a class.  And abandoned using the timeout facility in favour of allowing the timeouts to
come from guesillamail API instead and then specifying retries as applicaable.




"""


class TestGuerrilla:
    def __init__(self, specified_email_addr=None):
        """
        NB: GuerrillaMailSession does not get attributes (eg. session_id, email address) until one of the get_...() functions are called
        """
        log.info(f"INITIALISING {__name__}")
        self.email_client_name = "GuerillaMail"
        self.email_addr = specified_email_addr
        self.session = None

    def simulate_timeout(self, simulated_timeout=10):
        print(f"simulating timeout")
        time.sleep(simulated_timeout)
        print(f"simulated timeout copmplete. Raising DisposableEmailException")
        raise DisposableEmailException(
            "Simulatted Error connecting to email client")

 # --------------
    def retry_upon_error(timelimit_per_attempt = None):
        """ If timelimit specified then decorated function will keep retrying until timelimit is reached """
        def decorate(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if timelimit_per_attempt:
                    func_endtime = time.time() + timelimit_per_attempt
                    attempt = 0
                    while time.time() < func_endtime:
                        attempt += 1
                        try:
                            return await func(*args, **kwargs)
                        #  may be raised for any reason, regardless...
                        except Exception as e:
                            print(
                                f"Attempt {attempt}. Function ({__name__}) raised exception: {e}.")
                    print(".....ok there isnt any more time")
                else: # no timelimit
                    try:
                        return await func(*args, **kwargs)
                    #  may be raised for various reasons, regardless...
                    except Exception as e:
                        print(
                            f"NB:  Function ({__name__}) raised exception: {e}. but no timelimt set so only going once)...")
                raise DisposableEmailException(f"timelimit_per_attempt({timelimit_per_attempt}) exceeded...")                                                 
            return wrapper
        return decorate

    def as_async_to_thread(func):
        """ Wrap function as asyncio.to_thread """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            log.debug(f"(from as_async_to_thread) The wrapper is about to call {func} and pass args: {args} and kwargs: {kwargs}")
            return asyncio.create_task(asyncio.to_thread(func, *args, **kwargs))
        return wrapper

    def as_asyncio_wait_for(timeout_per_connect=10):
        """ 
        Decorarated func will try its task for [timeout]s and otherwise timeout.
        Acheived by wrapping function as asyncio.wait_for 
        """
        def decorate(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                awaitable_func = await func(*args, **kwargs)
                log.debug(f"(from as_asyncio_wait_for)The wrapper is about to call {func} and pass args: {args} and kwargs: {kwargs}")
                try:
                    return await asyncio.wait_for(awaitable_func, timeout=timeout_per_connect)
                except asyncio.TimeoutError as err:
                    log.warning(f'timeout! -{err}')
                    raise DisposableEmailException(
                        f"(from as_asyncio_wait_for): timeout_per_connect({timeout_per_connect})  Error connecting to email client")
            return wrapper
        return decorate

    # --------------
    # @DisposableEmail.catch_disposable_email_exception

    @retry_upon_error(3)
    @as_asyncio_wait_for(2)
    @as_async_to_thread
    def _connect(self, testing_var, *args, **kwargs):
        # print(f"1. inside <connect>  - with args: {testing_var}")
        # self.simulate_timeout(4)
        return GuerrillaMailSession(email_address=self.email_addr) if self.email_addr else GuerrillaMailSession()


    async def do_connect(self, testing_var):
        try:
            self.session = await self._connect(testing_var)
        except DisposableEmailException as e:
            log.warning(f"Error creating Client Session: {e}")
            raise DisposableEmailException(f"Error creating Client Session: {e}")


    @retry_upon_error(4)
    @as_asyncio_wait_for(1)
    @as_async_to_thread
    def _get_email_address(self, *args, **kwargs):
        return self.session.get_session_state()['email_address']

    async def do_get_email_address(self, *args, **kwargs) -> str:
        try:
            log.info("Attempting to return email")
            return await self._get_email_address(*args, **kwargs)
        except GuerrillaMailException as err:
            log.warning(f"Error getting email address: {err}")
            raise DisposableEmailException(f"Error getting email address: {err}")

    async def email_address(self, *args, **kwargs) -> str:
        # check if session is None then create a session
        if self.session is None:
            await self.do_connect('my_testing_var')
            print(f"session should now be present (otherwise and exc would have been raised): {self.session}")
        print(await self._get_email_address(*args, **kwargs))




if __name__ == '__main__':
    test = TestGuerrilla('')
    # for _ in range(3):
    asyncio.run(test.email_address())


# dec 1 - should wrap a blocking function in an asyncio.to_thread()
# dec 2 - should check retry on exception if user has specified a timeout
# dec 3 - should take a timeout and return a asyncio.wait_for which reties until timeout.
