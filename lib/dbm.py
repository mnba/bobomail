"Generic functions and classes for persisent databases"


# Standard module
from shelve import Shelf
# Own module
from util import atexit



def openPersistentDB(*args):
	"openPersistent(*args) -> shelf_instance"
	try:
		import gdbm
		db = apply(gdbm.open, args)
	except:
		import dumbdbm
		db = apply(dumbdbm.open, args)
	atexit(db.close)
	return Shelf(db)


class PersistentRecord:
	"""Subclass this and your class will automaticaly save all its attributes
	which are registeres in self.entries.keys()
	The corresponding self.entries.values() should contain default values.
	"""
	
	entries = {}

	def __init__(self, db, key=None):
		"""db should be a dictionary like type, e.g. a Shelf instance
		if key != None then the record with this key will be loaded
		"""
		self.key = key
		self.db = db
		for key, value in self.entries.items():
			self.__dict__[key] = value
		if self.key is not None:
			self._load()

	def __del__(self):
		self.save_pdict()

	def __setattr__(self, name, value):
		self.__dict__[name] = value
		if name in self.entries.keys():
			self.save_pdict()

	def _pdict(self): 
		data = {}
		for key, default in self.entries.items():
			data[key] = self.__dict__.get(key, default)
		return data

	def __repr__(self):
		return repr(self._pdict())

	def save_pdict(self):
		if self.key is not None:
			self.db[self.key] = self._pdict()
			
	def _load(self):
		try:
			data = self.db[self.key]
			for key, value in data.items():
				self.__dict__[key] = value
		except KeyError: pass
