"""Authentication module for BoboMail"""
import os

from session import Session
from user import User
from bobomailrc import DEBUG, true, false
from lib import connections


class Authentication:
	"more or less a abstract base class"
	
	def __init__(self, session):
		self.session = session

	def check(self, host, userid, password):
		return false # dummy-method  -  has to be overwritten

	def relogin(self):
		try:
			self.user = User(self.session.user)
			return true
		except:
			if DEBUG: raise
			else: return false

	def login(self, host, userid, password):
		if self.check(host, userid, password):
			self.user = User(userid, host)
			self.user.host = host
			self.user.id = userid
			self.session.user = self.user.key
			self.session.password = password
			return true
		else:
			if DEBUG: raise
			else: return false

	def logout(self):
		try: 
			self.session.expire()
			if hasattr(self, "con"):
				connections.close(self.con)
		except:
			if DEBUG: raise

	

class SimpleAuthentication(Authentication):

	atable = {
		"guest": "guest"
		}

	def check(self, host, userid, password):
		if self.atable.get(userid, None) == password:
			return true
		else:
			return false


from lib.pop3lib import POP3X
class POP3Authentication(Authentication):
	"authenticate against a pop server"

	def check(self, host, userid, password):
		try:
			self.con = connections.get(userid, password, host, "pop3")
			if self.con:
				connections.close(self.con)
			c = POP3X(host)
			self.con = connections.register(
				c, userid, password, host, "pop3", c.quit)
			self.con.query("user", (userid,))
			self.con.query("pass_", (password,))
			return true
		except:
			if self.con:
				connections.close(self.con)
			if DEBUG: raise
			else: return false
			


from imaplib import IMAP4
class IMAP4Authentication(Authentication):
	"authenticate against a imap server"
	
	def check(self, host, userid, password):
		try:
			self.con = connections.get(userid, password, host, "imap4")
			if self.con:
				connections.close(self.con)
			c = IMAP4(host)
			self.con = connections.register(
				c, userid, password, host, "imap4", c.logout)
			self.con.query("login", (userid, password))
			return true
		except: 
		    if DEBUG: raise
		    else: return false
		
#XXX TODO:
#class APOP3Authentication(Authentication): pass
#class PasswdFileAuthentication(Authentication): pass
#class HtAccessAuthentication(Authentication): pass

if __name__ == "__main__":
	a = IMAP4Authentication()
	print a.login("localhost", "guest", "guest")
	
