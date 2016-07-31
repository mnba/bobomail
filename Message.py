"""This module provides a mime message class for BoboMail"""

from bobomailrc import DateStrFormat, DateShortStrFormat

import lib.Message, string, rfc822, time

def dump_address_pair(pair):
	"""Dump a (name, address) pair in a canonicalized form."""
	if pair[0]:
		return '"%s" <%s>' %  (pair[0], pair[1] or "")
	else:
		return pair[1] or ""


class Message(lib.Message.Message):

	def __init__(self, *args, **kws):
		apply(lib.Message.Message.__init__, (self,)+args, kws)
		self.processHeaders()

	def processHeaders(self):
		"This adds some attributes to the object (Subject, Sender, ToList etc)"
		def makeaddrlist(addrs):
			return string.join(map(dump_address_pair, addrs or []), ", ")

		self.Lines = self["Lines"]
		if self.Lines: self.Lines = int(self.Lines)
		self.Subject = self["Subject"]
		self.FromName, self.FromAddr = self.getaddr("From")
		self.Sender = dump_address_pair(self.getaddr("From") or self.getaddr("Sender"))
		self.ReplyTo = dump_address_pair(self.getaddr("Reply-To"))
		self.ToList = makeaddrlist(self.getaddrlist("To"))
		self.CcList = makeaddrlist(self.getaddrlist("Cc"))
		self.BccList = makeaddrlist(self.getaddrlist("Bcc"))
		self.UserAgent = self["X-Mailer"] or self["User-Agent"]
		self.Date = self.getdate("Date")
		if self.Date:
			# Silly Y2k bug in some mailers
			if self.Date[0] > 99 and self.Date[0] < 200:
				self.Date = (self.Date[0] + 1900,) + self.Date[1:]
			try:
				self.DateStr = time.strftime(DateStrFormat, self.Date)
				self.DateShortStr = time.strftime(DateShortStrFormat, self.Date)
			except:
				self.DateStr = self.getheader("Date", "(no date)")
				self.DateShortStr = self.DateStr
		else:
			self.DateStr = self.DateShortStr = "(no date)"
