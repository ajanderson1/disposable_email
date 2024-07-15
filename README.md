# Disposable Email Interface

Simple Protocol implementation of a disposable email interface.  The concept is that the different email services can be plugged in without any changes to underlying code, and the user can interact with the email service in a standardised way.

##  GuerrilaMail

USEAGE:
Begin new session:
```python
my_inbox = GuerrillaMail('qfxfsveb@guerrillamailblock.com')
```
...or omit the email address for a random email address

```python
print(my_inbox.inbox_size)
print(my_inbox.list_inbox())
```
---

# Useful links
Blocked Email domains.
* https://github.com/disposable-email-domains/disposable-email-domains
* https://www.guerrillamail.com/GuerrillaMailAPI.html
* https://docs.google.com/document/d/1Qw5KQP1j57BPTDmms5nspe-QAjNEsNg8cQHpAAycYNM/edit?hl=en (Updated)
