# -*- coding: utf-8 -*-
"""This is the main module"""

#############################################
#                                           #
#                BoboMail                   #
#     http://bobomail.sourceforge.net       #
#  Distributed under GNU GPL. See COPYING   #
#  Copyright (c) 1998-2000 Henning Schröder #
#                                           #
#############################################

from init import *
from DocumentTemplate import HTML
from string import replace
from lib.util import getusername, urlunquote
from lib.logging import log

status_message = [
	"",
	i18n("Welcome! You successfully logged in"),
	i18n("Message sent without any problems"),
	i18n("Selected message(s) deleted"),
	i18n("Message bounced"),
	i18n("Selected message(s) copied"),
	i18n("Selected message(s) moved"),
	i18n("Folder created"),
	i18n("Folder renamed"),
	i18n("Folder deleted")
	]


from webapp import WebApp, SessionManager

from AddrBook import AddressBook
from Prefs import Preferences
from MailBox import MailBox

class BoboMail(WebApp):
	"BoboMail main class"

	def __init__(self, AuthClass, MBoxClass):
		WebApp.__init__(self, SessionManager(session_db_filename, max_session_length), template_template, "BoboMail")
		self.Authentication = AuthClass
		self.MailBox = MailBox(self, MBoxClass)
		self.Prefs = Preferences(self)
		self.AddrBook = AddressBook(self)

	def error(self, msg, reason=None):
		return self.genHTML(self.REQUEST, open(error_template), imagedir=image_dir,
							title=i18n("Error"), description=msg, reason=reason)
		
	def authError(self):
		log("FAILURE: authenticating", log_filename)
		return self.error(
			i18n("Authentication failed. Please check your userid and password" +
				 " and try to login again."), reason=i18n("Or maybe your session has expired"))
	
	def Restart(self, pw=""):
		"Restart persistent cgi"
		if pw == pcgi_password:
			print "Content-type: text/plain\n"
			import sys
			sys.path.insert(0, pathjoin(app_dir, "pcgi/Util"))
			from killpcgi import killpcgi
			killpcgi(pcgi_infofile)
		else:
			return '<form action="Restart"><input type="password" name="pw"><input type="submit" value="OK"></form>'

	def index_html(self, REQUEST, RESPONSE):
		"Show start page"
		if template_dir[-7:] == "/frames":
			RESPONSE.redirect("%s/frames" % REQUEST["SCRIPT_NAME"])
		return self.login_frame(REQUEST)
	
	def login_frame(self, REQUEST):
		"return login frame"
		return self.genHTML(REQUEST, open(login_template), imagedir=image_dir,
							title=i18n("Login"), multihosts=multihosts, hosts=allowed_hosts)

	def frames(self):
		"Return frameset"
		return open(frames_template).read()

	def Login(self, REQUEST, RESPONSE, userid, password, host=""):
		"Log into BoboMail"
		if multihosts: ahost = host
		else:
			ahost = auth_host
		auth = self.Authentication(REQUEST["SESSION"])
		if ((ahost in allowed_hosts) or (allowed_hosts == [])) \
		   and auth.login(ahost, userid, password):
			auth.user.name = auth.user.name or getusername(auth.user)
			if multihosts:
				auth.user.domain = auth.user.domain or \
								   multi_domain.get(ahost, domain)
			else:
				auth.user.domain = auth.user.domain or domain
			auth.user.signature = auth.user.signature or default_signature
			auth.user.maxlistsize = auth.user.maxlistsize or 20
			log("OK: %s logged in" % userid, log_filename)
			RESPONSE.redirect(
				"%s/MailBox/List?message:int=%s" % (REQUEST["SESSION_URL"], 1))
			#return self.MailBox.List(REQUEST, message=1)
		else: return self.authError()
						 
	def About(self, REQUEST):
		"About bobomail"
		return self.genHTML(REQUEST, open(about_template), imagedir=image_dir,
							title=i18n("About"), version=bobomail_version)

	def Help(self):
		"Help for bobomail"
		return i18n("Only loosers and communists need help (Weird Al Yankovic)")

	def Homepage(self):
		"Show project homepage"
		import makehtml
		return makehtml.genPage()

	def GetFile(self, REQUEST, RESPONSE):
		"Get file (if you use BoboMailHTTPServer)"
		import os
		fn = urlunquote(REQUEST.get("QUERY_STRING", ""))
		if fn[0] not in [".", os.sep]:
			import mimetypes
			mimetypes.init(["/etc/mime.types", bm_mimetypes])
			ext = os.path.splitext(fn)[1]
			ctype = mimetypes.guess_type(ext)[0] or "application/octet-stream"
			RESPONSE.setHeader("Content-Type", ctype)
			return open(os.path.join(app_dir, fn)).read()

	def Logout(self, REQUEST, RESPONSE):
		"Log out"
		auth = self.Authentication(REQUEST["SESSION"])
		if auth.relogin(): auth.logout()
		auth.session.expire()
		RESPONSE.redirect("%s/index_html" % REQUEST["SCRIPT_NAME"])


class BoboMailDEBUG(BoboMail):
	"some extra functionality when debugging/developing"

	def Debug(self, REQUEST, RESPONSE):
		"Debug session"
		from string import join
		from lib import connections
		return join(map(str, connections.contable.values()), "\n") + \
			   "\n" + join(map(str, REQUEST.items()), "\n")


class BoboMailDemo(BoboMail):
	"disable some functionality - used on SourceForge demo"
	
	def SendMsg(self, sid, To, index, REQUEST, RESPONSE):
		"Bounce message to recipient"
		return "disabled in demo"

	def Send(self, REQUEST, RESPONSE, sid, to, cc="", bcc="", subject="", body="", attach=None, InReplyTo=None):
		"Send mail"
		return "disabled in demo"


if use_imap:
    from fetchmail import IMAP4Box
    from auth import IMAP4Authentication
    Box = IMAP4Box
    Auth = IMAP4Authentication
else:
    from fetchmail import POP3Box
    from auth import POP3Authentication
    Box = POP3Box
    Auth = POP3Authentication

Debug=True
if DEBUG:
	bobomail = BoboMailDEBUG(Auth, Box)
else:
	bobomail = BoboMail(Auth, Box)

bobo_application = bobomail # only publish bobomail instance

