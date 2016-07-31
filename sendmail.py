from mimetools import choose_boundary, encode
from string import split, join, replace, strip
import mimetypes, os

from lib.util import StringIO
from Message import Message
from bobomailrc import *

if smtp_host[0] == "/":
    from lib.pipesmtp import SMTP
else:
    from smtplib import SMTP

mimetypes.init(["/etc/mime.types", bm_mimetypes])

def makePart(body, encoding):
	msg = Message(StringIO())
	msg["Content-Transfer-Encoding"] =  encoding
	out = StringIO()
	if encoding != "base64":
		encode(StringIO(replace(body,"\r","")), out, encoding)
	else:
		encode(StringIO(body), out, encoding)
	msg.body = out.getvalue()
	if encoding == "quoted-printable":
		lines = split(msg.body, "\n")
		for i in xrange(len(lines)):
			if lines[i] and lines[i][:5] == 'From ':
				lines[i] = "=%02x" % ord("F") + lines[i][1:]
		msg.body = join(lines, "\n")
	return msg


class SentFailed:

	def __init__(self, e, c, r):
		self.email, self.code, self.reason = e, c, r

	def __repr__(self):
		return str((self.code, self.reason, self.email))


def sendmail(From, To, Cc=None, Bcc=None, Subject="", 
			 Body="", File=None, Filename="", InReplyTo=None):
	text = makePart(Body, "quoted-printable")
	if File is not None:
	    data = File.read()
	    if data:
		attach = makePart(data, "base64")
		ext = os.path.splitext(Filename)[1]
		ctype = mimetypes.guess_type(ext)[0] or "application/octet-stream"
		attach["Content-Type"] = ctype
		Filename = os.path.split(Filename)[1]
		attach["Content-Disposition"] = 'attachment; filename="%s"' % Filename
		msg = Message(StringIO())
		msg.boundary = choose_boundary()
		msg["Content-Type"] = 'multipart/mixed; boundary="%s"' % msg.boundary
		msg.parts.extend([text, attach])
	    else: msg = text
	else: msg = text
	msg["From"] = From
	msg["To"] = To
	if Cc: msg["Cc"] = Cc
	if Bcc: msg["Bcc"] = Bcc
	if InReplyTo: msg["In-Reply-To"] = InReplyTo
	msg["Subject"] = Subject or ""
	msg["Mime-Version"] = "1.0"
	text["Content-Type"] = "text/plain; charset=ISO-8859-1"
	msg["X-Mailer"] = XMailer
	Recipients = msg.getaddrlist("to") + msg.getaddrlist("cc") + msg.getaddrlist("bcc")
	for i in range(len(Recipients)):
	    Recipients[i] = Recipients[i][1]
	return sendMessage(From, Recipients, msg)

def sendMessage(From, ToList, msg):
	errors = [] #XXX handle smtplib.SMTPSenderRefused
	s = SMTP(smtp_host)
	failed = s.sendmail(From, ToList, str(msg))
	s.quit()
	for email, (code, reason) in failed.items():
		errors.append(SentFailed(email, code, reason))
	return errors


if __name__ == "__main__":
	print sendmail(
		"hs@cs.uni-ol.de", "henning@localhost", None, None, "Testmail",
		"From Hallo Leute\nGruﬂ Henning",
		open("/home/henning/src/bobomail/images/bobomail.jpg"), "bobomail.jpg")
	#print sendmail("hs@cs.uni-ol.de", "root@localhost", "benno@localhost", "henning@localhost",
	#			   "Testm‰l", "From Someone\nGruﬂ Henning")
