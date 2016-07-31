"""This module adds functionality to change the users's password.
It needs that the cgi runs setuid. So be very careful! Currently only for testing
"""

from bobomod import *

import main
PWD_CHANGED = len(main.status_message)
main.status_message.append(i18n("Password changed"))


class Passsword(BoboMailModule):
	"Password module for BoboMail"

	def index_html(self, sid):
		"Show change-password page"
		auth = self.Authentication()
		if auth.relogin(sid):
			return HTMLTemplate(main.password_template, title="Paßwort ändern", sid=sid)
		else: return authError()
		
	def Change(self, sid, pw, pw2, REQUEST, RESPONSE):
		"change password"
		auth = self.Authentication()
		if auth.relogin(sid):
			if pw != pw2:
				return HTMLTemplate(main.error_template, sid=sid, title="Fehler",
						    description="Paßwort konnte nicht geändert werden",
						    reason="Die beiden Eingaben stimmten nicht überein")
			else:
				cmd = "/usr/sbin/chpwd" 
				os.popen(cmd, "w").write("%s:%s\n" % (auth.user.id, pw))
				auth.session.password = pw
				RESPONSE.redirect("%s/List?sid=%s&message:int=%s" % (
					REQUEST["SCRIPT_NAME"], sid, PWD_CHANGED))

		else: return self.authError()
