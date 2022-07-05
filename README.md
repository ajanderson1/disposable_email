# Disposable Email Interface

Simple Protocol implementation of a disposable email interface.  The concept is that the different email services can be plugged in without any changes to underlying code.


4/7/22 - working on guerilla mail, faily undsstbale so need to build in a retry favilitiy to each method, perhaps a decoratro, which listens for the tiemout and then tries again if less that user-specified timeout.

### Useful links
Bloacked Email domains.
* https://github.com/disposable-email-domains/disposable-email-domains



Further Ideas.

could have jsut a genreric email client + disposable exmail extends it.
simploify/unify gmail interface using exisint libraries or imap libs
tpo satisfy basic proocl satill aiming to jsut

check (poll)( an emaill address for an email coming in that matches some criteria
returns email as standardised email object
gets size of inbox
gets its own email address
...perhaps sends an email. 