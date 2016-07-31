"""This modules handles tcp connections for the application protocolls (pop3, imap4, ..)
"""
# XXX: make code thread-safe!
from bobomailrc import connection_timeout, DEBUG
from util import atexit
from time import time 

contable = {}

def makeuid(userid, password, host, port):
	return "%s:%s@%s:%s" % (userid, password, host, port)


class Connection:
	
	def __init__(self, con, userid, password, host, port, closehandler):
		self.uid = makeuid(userid, password, host, port)
		self.con = con
		self.userid = userid
		self.password = password
		self.host = host
		self.port = port
		self.closehandler = closehandler
		self.lastused = time()

	def query(self, func, args):
		if DEBUG: open("/tmp/condebug", "a").write("%s %s\n" % (func, args))
		self.lastused = time()
		confunc = getattr(self.con, func)
		result = apply(confunc, args)
		if DEBUG: open("/tmp/condebug", "a").write(" -> %s\n" % repr(result))
		return result

	def __repr__(self):
		return "<Connection %s>" % makeuid(self.userid, "XXX", self.host, self.port)


def register(con, userid, password, host, port, closehandler):
	global contable
	c = Connection(con, userid, password, host, port, closehandler)
	contable[c.uid] = c
	return c

def get(userid, password, host, port):
	# XXX: side-effect close connections on timeout
	global contable
	for key in contable.keys():
		if contable[key].lastused > time() + connection_timeout:
			close(key)
	try:
		con = contable.get(makeuid(userid, password, host, port), None)
		if con: ok = con.query("noop", ())
		return con
	except:
		if DEBUG: raise

def close(con):
	global contable
	c = contable[con.uid]
	con.closehandler()
	del contable[con.uid]
	
def closeall():
	for key in contable.values():
		close(key)

atexit(closeall)

if __name__ == "__main__":
	from poplib import POP3
	for i in range(2):
		con = get("guest", "gast", "localhost", "pop3")
		if not con:
			c = POP3("localhost")
			c.user("guest")
			c.pass_("gast")
			con = register(c, "guest", "gast", "localhost", "pop3", c.quit)
		print con, con.getcon()
	
