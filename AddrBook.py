from bobomailrc import addrs_template
from lib.util import urlquote
from string import join
from bobomod import *

class AddressBook(BoboMailModule):
	"Address book class for BoboMail"

	def index_html(self, REQUEST):
		"Address book"
		class Adress: pass
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		addrs = []
		for entry in auth.user.addrs: 
			a = Adress()
			a.__dict__ = entry
			addrs.append(a)
		return self.genHTML(REQUEST, open(addrs_template),
							title=i18n("Address book"), addrs=addrs)

	def Send(self, REQUEST, RESPONSE):
		"Send Mail to selected recipents"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		import cgi
		form = cgi.FieldStorage()
		addrs = form.keys()
		tos, ccs, bccs = [], [], []
		for a in addrs:
			field, number = a[:3], int(a[3:])
			addr = '"%(username)s" <%(email)s>' % auth.user.addrs[number]
			if field == "to_":
				tos.append(addr)
			elif field == "cc_":
				ccs.append(addr)
			elif field == "bc_":
				bccs.append(addr)
		qs = ""
		if tos:
			qs = "&To=%s" % urlquote(join(tos, ", "))
		if ccs:
			qs = "%s&Cc=%s" % (qs, urlquote(join(ccs, ", ")))
		if bccs:
			qs = "%s&Bcc=%s" % (qs, urlquote(join(bccs, ", ")))
		RESPONSE.redirect("%s/MailBox/Compose?%s" % (REQUEST["SESSION_URL"], qs))

	def Add(self, REQUEST, RESPONSE, username, email):
		"Add to address book"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		addrs = auth.user.addrs
		addrs.append({"username": username, "email": email})
		auth.user.addrs = addrs
		RESPONSE.redirect("%s/AddrBook/index_html" % REQUEST["SESSION_URL"])

	def Del(self, REQUEST, RESPONSE, num):
		"Delete from address book"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		addrs = auth.user.addrs
		del addrs[int(num)]
		auth.user.addrs = addrs
		RESPONSE.redirect("%s/AddrBook/index_html" % REQUEST["SESSION_URL"])

