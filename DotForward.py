"""This module provides an interface to the user's .forward.
It needs that the cgi runs setuid. So be very careful! Currently only for testing
"""

from string import split, join, strip
from UserList import UserList

class DotForwardFile(UserList):
	"This class provides a list-like interface to a .forward"

    def __init__(self, f=None, procmail=""):
        UserList.__init__(self)
        if procmail: self.procmail = "|%s " % procmail
        else: self.procmail = ""
        self.pmlen = len(self.procmail)
        self.addrs = self.data
        if f:
            if hasattr(f, "read"): self.parse(f.read())
            else: self.parse(f)

    def _unquote(self, s):
        if len(s) > 1 and s[0] in ["'", '"'] and s[-1] == s[0]:
            return s[1:-1]
        else: return s

    def _quote(self, s):
        return '"%s"' % s

    def _unfilter(self, s):
        if s and s[:self.pmlen] == self.procmail:
            return s[self.pmlen:]
        else: return s

    def _filter(self, s):
        return "%s%s" % (self.procmail, s)
        
    def parse(self, data):
        for line in split(data, "\n"):
            addrs = map(self._unfilter,
                        map(self._unquote,
                        map(strip, split(line, ","))))
            for a in addrs:
                if a: self.append(a)

    def __str__(self):
		"return a string which can be written to .forward"
        return join(map(self._quote, map(self._filter, self.addrs)), "\n")



def setuser(name):
	"change user for more security"
	try:
		entry = pwd.getpwnam(name)
		userid, groupid = entry[2:4]
		os.setgid(groupid)
		os.setuid(userid)
		return entry
	except: pass

def dot_forward(user):
	"return the filename with path of an user's .forward"
	userdata = setuser(user)
	if userdata:
		homedir = userdata[5]
		return "%s/.forward" % homedir

def read_forward(user):
	"returns a file object"
	dot_fwd = dot_forward(user)
	if dot_fwd:
		try:
			return open(dot_fwd).read()
		except IOError: pass
	return ""

def write_forward(user, addrs):
	"writes .forward"
	dot_fwd = dot_forward(user)
	if dot_fwd:
		try:
			open(dot_fwd, "w").write(addrs.read())
		except IOError: pass



import main
FWD_CHANGED = len(main.status_message)
main.status_message.append(i18n(".forward changed"))


from bobomod import *


class DotForward:
	"Class to manage user's ~/.forward in BoboMail"

	def __init__(self, parent):
		self.bobomail = parent

	def index_html(self):
		"Setup .forward"
		auth = self.bobomail.Authentication()
		if auth.relogin(sid):
			data = read_forward(auth.user.id)
			addrs = DotForward(data, procmail)
			if auth.user.id in addrs:
				keepcopy = 1
				addrs.remove(auth.user.id)
			else: keepcopy = 0
			return HTMLTemplate(forwardaddr_template, keepcopy=keepcopy,
								forwardto=string.join(addrs, ","),
								title="Weiterleitungen konfigurieren", sid=sid)
		else: return authError()

	def Change(self, sid, REQUEST, RESPONSE, keepcopy="off", forwardto=""):
		"Change .forward"
		auth = self.bobomail.Authentication()
		if auth.relogin(sid):
			fwd = DotForward(forwardto, procmail)
			if auth.user.id in fwd:
				fwd.remove(auth.user.id)
			addrs = str(fwd)
			if keepcopy == "on" and addrs:
				addrs = "%s\n%s" % (auth.user.id, addrs)
			write_forward(auth.user.id, addrs)
			RESPONSE.redirect("%s/List?sid=%s&message:int=%s" % (
				REQUEST["SCRIPT_NAME"], sid, FWD_CHANGED))
		else: return authError()
