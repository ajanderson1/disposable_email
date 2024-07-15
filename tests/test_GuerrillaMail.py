import pytest
from unittest.mock import patch, MagicMock
from disposable_email.GuerrillaMail import GuerrillaMail, DisposableEmailException
from email.message import EmailMessage
from datetime import datetime

@pytest.fixture
def guerrillamail_instance():
    return GuerrillaMail()

@pytest.fixture
def mock_email():
    email = MagicMock()
    email.subject = 'Test'
    email.sender = 'test@example.com'
    email.body = 'Test body'
    email.datetime = datetime.now()
    return email

def test_guerrillamail_init(guerrillamail_instance):
    assert guerrillamail_instance.email_client_friendly_name == "GuerillaMail"

@patch('disposable_email.GuerrillaMail.GuerrillaMailSession.get_session_state')
def test_guerrillamail_get_email_address(mock_get_session_state, guerrillamail_instance):
    mock_get_session_state.return_value = {'email_address': 'test@guerrillamailblock.com'}
    email_address = guerrillamail_instance.get_email_address()
    assert email_address == 'test@guerrillamailblock.com'

@patch('disposable_email.GuerrillaMail.GuerrillaMailSession.get_email_list')
def test_guerrillamail_inbox_size(mock_get_email_list, guerrillamail_instance):
    mock_get_email_list.return_value = [{'mail_id': '1'}, {'mail_id': '2'}]
    inbox_size = guerrillamail_instance.inbox_size
    assert inbox_size == 2

@patch('disposable_email.GuerrillaMail.GuerrillaMailSession.get_email_list')
def test_guerrillamail_list_inbox(mock_get_email_list, guerrillamail_instance):
    mock_email = MagicMock()
    mock_email.guid = '1'
    mock_email.__dict__ = {'guid': '1', 'subject': 'Test', 'sender': 'test@example.com', 'body': 'Test body'}
    mock_get_email_list.return_value = [mock_email]
    with patch.object(guerrillamail_instance.guerrillaSession, 'get_email', return_value=mock_email):
        inbox_list = guerrillamail_instance.list_inbox()
        assert isinstance(inbox_list, list)
        assert len(inbox_list) == 1
        assert inbox_list[0]['subject'] == 'Test'

@patch('disposable_email.GuerrillaMail.GuerrillaMailSession.get_email_list')
def test_guerrillamail_get_most_recent_email(mock_get_email_list, guerrillamail_instance):
    mock_email_element = MagicMock()
    mock_email_element.guid = '1'
    mock_email = MagicMock()
    mock_email.subject = 'Test'
    mock_email.sender = 'test@example.com'
    mock_email.body = 'Test body'
    mock_get_email_list.return_value = [mock_email_element]
    with patch.object(guerrillamail_instance.guerrillaSession, 'get_email', return_value=mock_email):
        most_recent_email = guerrillamail_instance.get_most_recent_email()
        assert isinstance(most_recent_email, EmailMessage)
        assert most_recent_email['Subject'] == 'Test'
        assert most_recent_email['From'] == 'test@example.com'
        

@patch('disposable_email.GuerrillaMail.GuerrillaMailSession')
def test_guerrillamail_await_next_email(MockGuerrillaMailSession, mock_email):
    # Setup
    mock_session = MockGuerrillaMailSession.return_value
    mock_session.get_session_state.return_value = {'email_address': 'test@guerrillamail.com'}
    
    from disposable_email.GuerrillaMail import GuerrillaMail
    guerrillamail_instance = GuerrillaMail()

    # Mock the initial empty inbox, then an inbox with one email
    mock_session.get_email_list.side_effect = [[], [MagicMock(guid='1')]]
    
    # Mock the email retrieval
    mock_session.get_email.return_value = mock_email

    # Test
    with patch('disposable_email.GuerrillaMail.poll') as mock_poll:
        mock_poll.return_value = MagicMock(guid='1')
        next_email = guerrillamail_instance.await_next_email(timeout=1)

    # Assertions
    assert isinstance(next_email, EmailMessage)
    assert next_email['Subject'] == 'Test'
    assert next_email['From'] == 'test@example.com'
    assert next_email['To'] == 'test@guerrillamail.com'
    
    # Verify that poll was called with the correct arguments
    mock_poll.assert_called_once()
    args, kwargs = mock_poll.call_args
    assert kwargs['step'] == 5
    assert kwargs['timeout'] == 1
    assert callable(args[0])  # First argument should be a lambda function

    # Verify that get_email was called with the correct guid
    mock_session.get_email.assert_called_once_with('1')


def test_guerrillamail_wrap_email(guerrillamail_instance):
    mock_email = MagicMock()
    mock_email.subject = 'Test'
    mock_email.sender = 'test@example.com'
    mock_email.body = 'Test body'
    wrapped_email = guerrillamail_instance.wrap_email(mock_email)
    assert isinstance(wrapped_email, EmailMessage)
    assert wrapped_email['Subject'] == 'Test'
    assert wrapped_email['From'] == 'test@example.com'
    assert wrapped_email.get_content().strip() == 'Test body'  # Using strip() to remove any leading/trailing whitespace