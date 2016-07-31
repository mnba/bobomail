"""This module provides a list-like interface to mail messages from several sources"""

import os
from string import split, join, find
from lib.pop3lib import POP3X
from mailbox import UnixMailbox #, _Subfile
from fetchmail_mailbox_Subfile import _Subfile #FIXME

from lib.util import StringIO, bytesizestr
from Message import Message


from bobomailrc import pop3_host, imap4_host, false

from lib import connections

class UnixMailspool(UnixMailbox):
	"The unix way - handles mails via /var/spool/mail/username"

	def __init__(self, filename=""):
		self.fp = None
		self.seekp = 0
		self.filename = filename
		self.connected = 0

	def __del__(self):
		try: self.fp.close()
		except: pass
		
	def open(self, auth):
		self.filename = "/var/spool/mail/%s" % auth.user.id
		self.fp = open(self.filename)
		self.auth = auth
		self.parse()
		self.connected = 1

	def parse(self):
		self.msgs = []
		while 1:
			m = self.next()
			if not m: break
			m.unique_num = len(self.msgs)
			self.msgs.append(m)

	def __call__(self, *args):
	    for i in range(len(self.msgs)):
		m = self.msgs[i]
		s = m.fp.stop - m.fp.start
		self.msgs[i].Size = s
		self.msgs[i].SizeStr = "%s" % bytesizestr(s)
            return self.msgs

	def folders(self): return ["INBOX"]
	def chdir(self, name): pass

	def __len__(self):
		return len(self.msgs)

	def __getitem__(self, index):
		if type(index) == type(()): index, preview = index
		else: preview = false
		if not preview: self.msgs[index].parse()
		return self.msgs[index]

	def __delitem__(self, index):
		newfn = "%s.new" % self.filename
		new = MailboxList(newfn)
		for i in range(len(self)):
			if i <> index:
				new.append(self[i])
		os.remove(self.filename)
		os.rename(newfn, self.filename)
		self.msgs = new.msgs
		self.fp = new.fp

	def next(self):
		while 1:
			self.fp.seek(self.seekp)
			try:
				self._search_start()
			except EOFError:
				self.seekp = self.fp.tell()
				return None
			start = self.fp.tell()
			self._search_end()
			self.seekp = stop = self.fp.tell()
			if start <> stop: break
		return Message(_Subfile(self.fp, start, stop), preview=1)

	def append(self, msg):
		self.fp.seek(1,2)
		if self.fp.read(1) <> '\n':
			self.fp.write('\n')
		self.fp.write(msg.unixfrom)
		self.fp.write(str(msg))

	def close(self): pass


class POP3Box:
	"This class is currently used in BoboMail to access mail"
	
	def __init__(self): self.connected = 0

	def open(self, auth):
		user = auth.user
		session = auth.session
		host = user.host or pop3_host
		self.con = connections.get(user.id, session.password, host, "pop3")
		if not self.con:
			c = POP3X(host)
			self.con = connections.register(
				c, user.id, session.password, host, "pop3", c.quit)
			self.con.query("user", (user.id,))
			self.con.query("pass_", (session.password,))
		self.connected = 1

	def folders(self): return ["INBOX"]
	def chdir(self, name): pass

	def __len__(self):
		return self.con.query("stat", ())[0]

	def __call__(self, *args):
		msgcount = len(self)
		if msgcount == 0: return []
		msgs = []
		ok, sizes, dummy = self.con.query("list", ())
		for i in range(msgcount):
			m = self[i, 1]
			m.Size = int(split(sizes[i], " ")[1])
			m.SizeStr = bytesizestr(m.Size)
			msgs.append(m)
		return msgs

	def chdir(self, name):
		pass 
	
	def __getitem__(self, index):
		"""returns a message object
		index can be a tuple - in this case the second element is a flag
		for only returning the headers (faster) """
		if type(index) == type(""):
			self.chdir(index)
			return self
		if type(index) == type(()): index, preview = index
		else: preview = false
		index = index + 1
		if preview:
			m = Message(self.con.query("top", (index, 0))[1], preview)
		else: m = Message(self.con.query("retr", (index,))[1], preview)
		m.unique_num = index - 1
		return m

	def __delitem__(self, index):
		self.con.query("dele", (index + 1,))

	
from imaplib import IMAP4
class IMAPException:
	def __init__(self, parent, msg):
		self.msg = msg
		parent.last_exception = self
	def __repr__(self): return repr(self.msg)
	def __str__(self): return str(repr(self))
	
class IMAP4Box:

	def __init__(self):
		self.connected = 0

	def open(self, auth):
		host = auth.user.host or imap4_host
		self.auth = auth
		user = auth.user
		session = auth.session
		self.con = connections.get(user.id, session.password, host, "imap4")
		if not self.con:
			c = IMAP4(host)
			self.con = connections.register(
				c, user.id, session.password, host, "imap4", c.logout)
			self.con.query("login", (auth.user.id, session.password))
		self.connected = 1

	def folders(self):
		ok, resp = self.con.query("list", ("Mail",))
		mailboxes = ["INBOX"]
		for line in resp:
			if not line: continue
			items = split(line)
			if "(\NoSelect)" not in items[:-1]:
				name = items[-1]
				mailboxes.append(name)
		return mailboxes

	def chdir(self, name):
		if getattr(self, "pwd", None) == name:
			return
		try: ok, resp = self.con.query("close")
		except: pass
		try:
			ok, resp = self.con.query("select", (name,))
		except: # Read-only?
			ok, resp = self.con.query("select", (name,1))
		self.folder_size = int(resp[0])
		self.pwd = name

	def append(self, num, folder=""):
		if type(num) == type(""):
			folder = num
			ok, resp = self.con.query("create", (folder,))
			if ok != "OK": raise IMAPException(self, resp)
		else:
			ok, resp = self.con.query("copy", (num, folder))

	def remove(self, folder):
		ok, resp = self.con.query("delete", (folder,))
		if ok != "OK": raise IMAPException(self, resp)
		
	def __len__(self):
		return self.folder_size

	def __delitem__(self, index):
		if type(index) == type(""):
			self.chdir(index)
			return self
		ok, msg = self.con.query("store", (str(index), 'FLAGS', '(\Deleted)'))
		if ok == "OK":
			self.con.query("expunge", ())

	def __setitem__(self, folder, newname):
		ok, resp = self.con.query("rename", (folder,newname))
		if ok != "OK": raise IMAPException(self, resp)
		
	def __call__(self):
		msgs = []
		for i in range(1,len(self)+1):
			m = self[i, 1]
			msgs.append(m)
		return msgs

	def __getitem__(self, index):
		if type(index) == type(""):
			self.chdir(index)
			return self
		if type(index) == type(()): index, preview = index
		else: preview = false
		if preview: resp, data = self.con.query("fetch", (index, '(FLAGS RFC822.HEADER RFC822.SIZE)'))
		else: resp, data = self.con.query("fetch", (index, '(FLAGS RFC822 RFC822.SIZE)'))
		m = Message(StringIO(data[0][1]), preview)
		m.unique_num = int(index)
		m.Size = int(data[1][find(data[1], "RFC822.SIZE")+11:-1])
		m.SizeStr = bytesizestr(m.Size)
		return m


        
	    

