# bobomail
Bobomail made to work, an archaic webmail-on-Python project of 2002 

Original project URL: https://sourceforge.net/projects/bobomail/

It had many bugs from point of view of modern Python 2.7 and of ZPublisher of Zope

Regretefully it doesn't support IMAP, nor POP3 with SSL, so it remains useless to me at the moment

***
Just some notes on place of bugs:

This Bobomail project uses ZOPE, and particularly ZPublisher in very specific way,
 using so called  __bobo_traverse__(self, request, key) interface function,
 And here there were a strong bug, which the original author implemented calling it 
 "# Some magic ;-) URLs without session-id will be redirected"

 More about __bobo_traverse__ function of ZPublisher can be read at:
 https://docs.zope.org/zope2/zdgbook/ObjectPublishing.html

But seems I have finally win the bug, at least I hope so.
***

Many other notes on patches for modern platforms are available in _Desc-MA.txt file.

URL to open on local machine:  http://localhost:9673/

---

 -Minas Abrahamyan 2016-07-31
