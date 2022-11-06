# Disposable Email Interface

Simple Protocol implementation of a disposable email interface.  The concept is that the different email services can be plugged in without any changes to underlying code.

## Testing GuerrilaMail

USEAGE:
Begin new session:
```
test = GuerrillaMail('qfxfsveb@guerrillamailblock.com')
```
or omit the email address for a random email address

print(test.inbox_size)
print(test.list_inbox())

Full GuerrrillaMail API documentation:
https://www.guerrillamail.com/GuerrillaMailAPI.html
https://docs.google.com/document/d/1Qw5KQP1j57BPTDmms5nspe-QAjNEsNg8cQHpAAycYNM/edit?hl=en (Updated)
\n



# Useful links
Bloacked Email domains.
* https://github.com/disposable-email-domains/disposable-email-domains



# Further Ideas.

could have jsut a genreric email client + disposable exmail extends it.
simploify/unify gmail interface using exisint libraries or imap libs
tpo satisfy basic proocl satill aiming to jsut

check (poll)( an emaill address for an email coming in that matches some criteria
returns email as standardised email object
gets size of inbox
gets its own email address
...perhaps sends an email. 