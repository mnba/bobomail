"""User database for BoboMail"""

from lib.dbm import PersistentRecord, openPersistentDB
from bobomailrc import user_db_filename

class User(PersistentRecord):
	entries = {
		"id":"", "name": "", "sortby":"", "signature": "", "newmsgs":[],
		"domain":"", "host":"", "inlineimages": "on", "addrs": [],
		"maxlistsize": 20}

	def __init__(self, id=None, host=None):
		if id and host:
			id = "%s@%s" % (id, host)
		PersistentRecord.__init__(self, userdb, id)

	def load(self):
		try:
			PersistentRecord.load(self)
		except KeyError: pass

	def save(self):
		if not self.id and self.host: return
		self.key = "%s@%s" % (self.id, self.host)
		PersistentRecord.save(self)


userdb = openPersistentDB(user_db_filename, "cw")
