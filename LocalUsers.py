"""This module provides a mail adress list of local users
It was mainly implemented for own purposes.
"""

from bobomailrc import users_template
from main import BoboMailModule, HTMLTemplate, _, authError


class LocalUsers(BoboMailModule):

	def Users(self, sid):
		"Show local users"
		def getlocalusers(domain="localhost", exclude=[]):
			class User: pass
			import pwd
			users = []
			for entry in pwd.getpwall():
				user, passoword, uid, gid, name, home, shell = entry
				if uid >= 500 and shell == "/bin/bash" and user not in exclude and name:
					u = User()
					u.name = name or None; u.email = "%s@%s" % (user, domain)
					users.append(u)
			return users
		auth = self.Authentication()
		if auth.relogin(sid):
			return HTMLTemplate(users_template, title="Mitglieder", sid=sid,
					    users=getlocalusers(auth.user.domain,
											["guest", "info", "nobody"]))
		else: return authError()
