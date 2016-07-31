"""Two simple classes for session management"""

# Standdard modules
import md5, mimetools, time, string
# Own module
from lib.dbm import PersistentRecord, openPersistentDB



class SessionExpired:
	"Throws exception when an expired session gets touched"
	pass

class SessionManager:
	"""This class will handle all sessions
	It has a dictionary-like interface with functions like
	  keys(), values(), items() and get(key, *default)"""

	def __init__(self, dbfilename, maxtime):
		"""Contructor has to be called with persistent database filename and
		max session length"""
		self.filename = dbfilename
		self.maxtime = maxtime
		self.db = openPersistentDB(self.filename, "wc")
		self.sessions = {}
		self.keys = self.sessions.keys
		self.values = self.sessions.values
		self.items = self.sessions.items
		self.get = self.sessions.get
		self.__getitem__ = self.get
		
	def new(self, initial_data={}, request={}):
		"new(initial_data) -> session_id"
		now = time.time()
		for x in self.keys():
			if self[x].death_time > now:
				self[x].expire()
		sess = Session(self)
		sid = sess.new()
		self.sessions[sid] = sess
		return sess

	def load(self, id):
		"Loads a previously created session. If the session expired a SessionEpiredException is thrown"
		if self.sessions.has_key(id):
			return self.sessions[id]
		sess = Session(self, id)
		if time.time() > sess.death_time:
			sess.expire()
			raise SessionExpired()
		else:
			self.sessions[id] = sess
		return sess

class Session(PersistentRecord):
	"This class handles a single session"

	entries = {
		"id":0 , "death_time":0, "extra_data": {}, "remote": "", "user": "", "password": ""}

	def __init__(self, session_manager, id=None):
		"Constructor can optionally be called with id to load a session"
		self.session_manager = session_manager
		self.maxtime = self.session_manager.maxtime
		PersistentRecord.__init__(self, self.session_manager.db, id)

	def expire(self):
		"Delete this session instance"
		try:
			self.extra_data = {} # Silly - just to be safe
			self.password = ""
			del self.session_manager.db[self.id]
			del self.session_manager.sessions[self.id]
		except: pass

	def genKey(self):
		"""genKey(self) -> key
		Generates unique key and returns it as a hex-string. It is called from self.new()"""
		hash = md5.new()
		hash.update(mimetools.choose_boundary())
		key = map(hex, map(ord, hash.digest()))
		key = string.replace(string.join(key, ""), "0x", "")
		return key

	def new(self, **extra):
		"""new(self, extra=None) -> new_id
		Creates a new session. extra can be a dict with initial session data"""
		for key, value in extra.items():
			setattr(self, key, value)
		self.death_time = self.maxtime + time.time()
		self.id = self.genKey()
		self.key = self.id
		return self.id

	#def __repr__(self):
	#	return "<Session %s>" % getattr(self, "id", "None")
