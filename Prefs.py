"""This module provides a webinterface to the user's preferences
   Here you can change username, signature etc"""

from bobomailrc import prefs_template
from string import lower
from bobomod import *

import main
PREFS_CHANGED = len(main.status_message)
main.status_message.append(i18n("Preferences changed"))


class Preferences(BoboMailModule):
	"Preferences class for BoboMail"

	def index_html(self, REQUEST):
		"Show preferences page"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		return self.genHTML(REQUEST, open(prefs_template),
							title=i18n("Preferences"), user=auth.user)
		
	def Change(self, REQUEST, RESPONSE,
			   username="", signature="", inlineimages="", maxlistsize=20):
		"Change preferences"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		auth.user.name = username
		auth.user.signature = signature
		auth.user.inlineimages = (lower(inlineimages) == "on")
		auth.user.maxlistsize = maxlistsize
		RESPONSE.redirect(
			"%s/MailBox/index_html?message:int=%s" % (
			  REQUEST["SESSION_URL"], PREFS_CHANGED))
