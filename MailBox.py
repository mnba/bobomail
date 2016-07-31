"""This module is responsible for the web-intercation of the mail stuff

"""
from lib.util import quotedtext, urlunquote
from mimeviewer import getMIMEPart, MessageViewer
from Message import Message
from string import lower

from bobomod import *

from main import list_template, mail_template, compose_template
from main import bounce_template, sent_template
from main import status_message, image_dir
from main import use_imap

import os; pathsplit = os.path.split

class MailBox(BoboMailModule):
	"""MailBox class for BoboMail
	Probably the most important part
	"""

	def __init__(self, parent_arg, MailboxClass):
		BoboMailModule.__init__(self, parent_arg)
		self.Mailbox = MailboxClass

	def getMailbox(self, auth):
		"return mailbox"
		mb = self.Mailbox()
		mb.open(auth)
		return mb
		
	def getSender(self, auth):
	    "return valid From-header"
	    sender = auth.user.id
	    if "@" not in sender:
		sender = "%s@%s" % (sender, auth.user.domain)
	    if auth.user.name: 
		sender = '"%s" <%s>' % (auth.user.name, sender)
	    return sender

	def markmsg(self, auth, msg):
		"mark messages as new"
		newmsgs = auth.user.newmsgs
		msgid = msg.getheader("message-id")
		if msgid not in newmsgs:
			newmsgs.append(msgid)
			auth.user.newmsgs = newmsgs

	def unmarkmsg(self, auth, msg):
		"mark messages as read"
		newmsgs = auth.user.newmsgs
		msgid = msg.getheader("message-id")
		if msgid in newmsgs:
			newmsgs.remove(msgid)
			auth.user.newmsgs = newmsgs

	def List(self, REQUEST, qs=0, by="", lastBy="", message=0, folder="INBOX"):
		"Show mails"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		mbox = self.getMailbox(auth)[folder]
		msgs = mbox()
		newmsgs = auth.user.newmsgs
		for i in range(len(msgs)):
			msgid = msgs[i].getheader("message-id")
			if msgid not in newmsgs:
				msgs[i].isNew = 1
		auth.user.newmsgs = newmsgs
		if not by:
			sby = auth.user.sortby
			if sby: by, reversed = sby
			else: by, reversed = "Date", "reverse"
			lastBy = by
		else:
			if by == lastBy: lastBy, reversed = "", "reverse"
			else: lastBy, reversed = by, ""
		auth.user.sortby = (by, reversed)
		folders = mbox.folders()
		return self.genHTML(REQUEST, open(list_template),
							{"%(by)s": by, "%(reversed)s": reversed,
							 "%(listsize)s": str(auth.user.maxlistsize)},
							mails=msgs, qs=qs, lastBy=lastBy,
							folders=folders, folder=folder,
							message=status_message[message],
							supports_folders=use_imap,
							title=i18n("List %(folder)s for %(user)s") % 
							      { "folder": folder,
									"user": (auth.user.name or auth.user.id)})

	index_html = List

	def Read(self, REQUEST, index, folder="INBOX"):
		"Read single message"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		mbox = self.getMailbox(auth)[folder]
		msg = mbox[index]
		self.markmsg(auth, msg)
		return self.genHTML(REQUEST, open(mail_template), folder=folder, folders=mbox.folders(),
							title=i18n("Read message"), msg=msg, index=index,
							supports_folders=use_imap,						
							message=MessageViewer(msg, folder=folder, inlineimages=auth.user.inlineimages))

	def GetPart(self, REQUEST, RESPONSE, index, num, folder="INBOX"):
		"Get decodes message part"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		mbox = self.getMailbox(auth)[folder]
		msg = mbox[index]
		if num != "":
			part = getMIMEPart(msg, num)
		else:
			part = msg
		RESPONSE.setHeader("Content-Type", part.gettype())
		if part.filename:
			RESPONSE.setHeader("Content-Disposition", 
							   'filename="%s"' % part.filename)
		return part.decode()

	def Compose(self, REQUEST, To="", Subject="", Cc="", Bcc=""):
		"Compose new message"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		if auth.user.signature:
			sig = "\n\n-- \n%s" % auth.user.signature
		else: sig = ""
		sender = self.getSender(auth)
		return self.genHTML(REQUEST, open(compose_template), body=sig,
							sender=sender, to=To, cc=Cc, bcc=Bcc, subject=Subject, 
							title=i18n("Compose new message"))


	def Reply(self, REQUEST, index, toAll=0, folder="INBOX"):
		"Reply to message" # XXX: make use of Reply-To header!
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		mbox = self.getMailbox(auth)[folder]
		msg = mbox[index]
		self.markmsg(auth, msg)
		if toAll: 
			cc = msg.ToList or ""
			if cc: cc = cc + ", "
			cc = cc  + msg.CcList or ""
		else: cc = ""
		subject = msg.Subject
		if subject and len(subject) >= 3:
			if lower(subject)[:3] not in ["re:", "aw:"]:
				subject = i18n("Re: %s") % subject
		else: subject = i18n("Re: %s") % subject
		sender = self.getSender(auth)
		return self.genHTML(REQUEST, open(compose_template), title=i18n("Reply to message"), 
							sender=sender, cc=cc, to=msg.Sender, subject=subject, 
							inreplyto=msg.getheader("message-id", ""),
							body=quotedtext(repr(MessageViewer(msg,folder=folder, inlineimages=0))))

	def ReplyAll(self, REQUEST, index, folder="INBOX"):
		"Reply to all recipients from message"
		return self.Reply(REQUEST, index, toAll=1, folder=folder)
	
	def ViewRaw(self, REQUEST, RESPONSE, index, headers=0, folder="INBOX"):
		"Show plain message"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		mbox = self.getMailbox(auth)[folder]
		msg = mbox[index,headers]
		self.markmsg(auth, msg)
		RESPONSE.setHeader("Content-type", "text/plain")
		return str(msg)

	def Forward(self, REQUEST, index, folder="INBOX"):
		"Forward a message"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		mbox = self.getMailbox(auth)[folder]
		msg = mbox[index]
		self.markmsg(auth, msg)
		sender = self.getSender(auth)
		return self.genHTML(
			REQUEST, open(compose_template), title=i18n("Forward message"), 
			sender=sender, subject=i18n("Fwd: %s - %s") % (msg.FromAddr, msg.Subject),
			body=quotedtext(repr(MessageViewer(msg, folder=folder, inlineimages=0))))			

	def Action(self, REQUEST, RESPONSE, action="", 
			   index=None, folder="INBOX", destination="", delete=""):
		"Do something with selected mails"
		if delete != "": action = "delete"
		if action == "delete": delflag, copyflag, msgtext, destination = 1, 0, 3, folder
		elif action == "copy": delflag, copyflag, msgtext = 0, 1, 5
		elif action == "move": delflag, copyflag, msgtext = 1, 1, 6
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		mbox = self.getMailbox(auth)[folder]
		if index != None:
			msg = mbox[index,1]
			if copyflag: mbox.append(index, destination)
			if delflag: del mbox[index]
			self.unmarkmsg(auth, msg)
		elif destination != "":
			import cgi, re
			numpat = re.compile("^del([0-9]*)")
			form = cgi.FieldStorage()
			dellist = []
			for i in form.keys():
				if i == "delete": continue # XXX quick hack
				m = numpat.match(i)
				if m: dellist.append(int(m.group(1)))
			dellist.sort(); dellist.reverse()
			for i in dellist:
				msg = mbox[i, 1]				
				if copyflag: mbox.append(i, destination)
				if delflag: del mbox[i]
				self.unmarkmsg(auth, msg)
		RESPONSE.redirect("%s/MailBox/index_html?message:int=%s&folder=%s" % (
			REQUEST["SESSION_URL"], msgtext, destination))

	def Move(self, REQUEST, RESPONSE, index=None, folder="INBOX", destinaton=""):
		"Move messages"
		return self.Action(REQUEST, RESPONSE, "move", index, folder)

	def Copy(self, REQUEST, RESPONSE, index=None, folder="INBOX", destinaton=""):
		"Copy messages"
		return self.Action(REQUEST, RESPONSE, "copy", index, folder)

	def Delete(self, REQUEST, RESPONSE, index=None, folder="INBOX"):
		"Delete messages"
		return self.Action(REQUEST, RESPONSE, "delete", index, folder)

	def Bounce(self, REQUEST, index, folder="INBOX"):
		"Bounce messages"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		return self.genHTML(REQUEST, open(bounce_template),
							title=i18n("Bounce message"), index=index)

	def SendMsg(self, REQUEST, RESPONSE, To, index):
		"Bounce message to recipient"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		inbox = self.getFolder(auth, "inbox")
		msg = inbox[index]
		sender = self.getSender(auth)
		from sendmail import *
		errors = sendMessage(sender, To, msg)
		if errors: 
			return self.genHTML(REQUEST, open(sent_template),
								title=i18n("Sent mail"), failed=errors)
		else:
			RESPONSE.redirect(
				"%s/MailBox/index_html?message:int=%s" % (
				REQUEST["SESSION_URL"], 5))
			
	def Send(self, REQUEST, RESPONSE, to, cc="", bcc="", subject="", body="", attach=None, InReplyTo=None):
		"Send mail"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		if InReplyTo: InReplyTo = urlunquote(InReplyTo)
		from sendmail import *
		filename = getattr(attach, "filename", "")
		if filename == "": attach = None # XXX: fix for Opera/Linux
		sender = self.getSender(auth)
		errors = sendmail(sender, to, cc, bcc,
						  subject, body, attach, filename, InReplyTo)
		if errors: 
			return self.genHTML(REQUEST, open(sent_template),
								title=i18n("Sent mail"), failed=errors)
		else:
			RESPONSE.redirect(
				"%s/MailBox/index_html?message:int=%s" % (
				REQUEST["SESSION_URL"], 2))

	def Goto(self, REQUEST, RESPONSE):
		"Goto URL (necessary to hide REFERRER information"
		url = urlunquote(REQUEST.get("QUERY_STRING", ""))
		RESPONSE.redirect(url)

	def Folder(self, REQUEST, RESPONSE, action, name, folder):
		"Folder management"
		auth = self.bobomail.Authentication(REQUEST["SESSION"])
		if not auth.relogin(): return self.authError()
		mbox = self.getMailbox(auth)
		if action == "create":
			name = "%s/%s" % (pathsplit(folder)[0], name)
			try:
				mbox.append(name)
				folder = name
				msgtext = 7
			except:
				return self.error(i18n("Folder could not be created"),
								  i18n("Probably you used invalid charakters") + \
								  "<br>%s" % mbox.last_exception)				
		elif action == "rename":
			name = "%s/%s" % (pathsplit(folder)[0], name)
			try:
				mbox[folder] = name
				msgtext = 8
				folder = name
			except:
				return self.error(i18n("Folder could not be renamed"),
								  i18n("Probably you used invalid charakters") + \
								  "<br>%s" % mbox.last_exception)				
		elif action == "delete":
			if name == os.path.split(folder)[1]:
				try:
					mbox.remove(folder)
					folder = "INBOX"
					msgtext = 9
				except:
					return self.error(i18n("Folder could not be removed"),
									  i18n("Perhaps the folder is already removed") + \
									  "<br>%s" % mbox.last_exception)
			else:
				return self.error(
					i18n("Folder NOT deleted"), i18n("You didn't type the name to confirm"))
		RESPONSE.redirect(
			"%s/MailBox/index_html?message:int=%s&folder=%s" % (
			REQUEST["SESSION_URL"], msgtext, folder))
