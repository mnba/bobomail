import os, re
from string import split, join, find, replace, lower, atoi
from urlparse import urljoin
from htmlentitydefs import entitydefs
from htmllib import HTMLParser
from sgmllib import SGMLParser
from formatter import AbstractFormatter, DumbWriter, NullFormatter

from DocumentTemplate import HTMLFile
import gttag

from Message import Message
from lib.util import escape, path2pid, pid2path, urlquote, urlunquote, StringIO
from bobomailrc import *


from fintl import gettext
_ = gettext



class HTML2TextParser(HTMLParser):

	def handle_image(self, src, alt, *args):
		if alt == "(image)": alt = "[%s]" % os.path.basename(src)
		self.handle_data(alt)

	def anchor_end(self):
		if self.anchor: self.anchor = None

	def end_title(self):
		HTMLParser.end_title(self)
		self.formatter.add_literal_data(self.title)
		self.formatter.add_hor_rule()
		self.formatter.add_line_break()

	def start_tr(self, attrs): self.unknown_starttag("tr", attrs)
	def end_tr(self): self.do_br([])

	
def getMIMEPart(msg, path=[]):
	if type(path) == type(""): path = pid2path(path)
	for p in path:
		if msg.gettype() == "message/rfc822":
			msg = Message(StringIO(msg.decode()))
		msg = msg.parts[p]
	return msg


class MIMEViewer:

	def __init__(self, msg, **kws):
		self.msg = msg
		if not hasattr(self.msg, "path"):
			self.msg.path = []
		self.kws = kws
		for key, value in kws.items():
			setattr(self, key, value)
		
	def toHTML(self):
		html = HTMLFile(mime_template)
		return html(
			index=self.msg.unique_num, num=path2pid(self.msg.path), folder=self.folder,
			imagedir=image_dir, filename=self.msg.filename, mimetype=self.msg.gettype())

	def toText(self):
		o = StringIO()
		f = AbstractFormatter(DumbWriter(o))
		p = HTML2TextParser(f)
		p.feed(str(self))
		p.close() # XXX hack
		return replace(replace(o.getvalue(), "[%s]" % _("Add to address book"), ""),
					   "[%s]" % _("Click to download"), "")

	def __repr__(self):
		return self.toText() or _("(no body)")

	def __str__(self): 
		return self.toHTML() or _("(no body)")


class MultiViewer(MIMEViewer):
	
	def toHTML(self):
		body = ""
		for i in range(len(self.msg.parts)):
			p = self.msg.parts[i]
			p.unique_num = self.msg.unique_num
			p.path = self.msg.path + [i]
			body = "%s%s" % (body, getBody(p, self.kws)) + '<br><!--<hr height="3"><br>-->'
		return body


class AlternativeViewer(MIMEViewer):

	prefer = ["text/html"]
	
	def toHTML(self):
		viewable = None
		for i in range(len(self.msg.parts)):
			p = self.msg.parts[i]
			p.unique_num = self.msg.unique_num
			p.path = self.msg.path + [i]
			ctype = p.gettype()
			if hasMIMEViewer(ctype):
				if ctype == "multipart/related":
					for x in p.parts:
						ct = x.gettype()
						if ct in self.prefer:
							ctype = ct
							break
				if not viewable or ctype in self.prefer:
					viewable = p
		if viewable:
			return getBody(viewable, self.kws)
		else:
			return MultiViewer(self.msg)


class RelatedViewer(MIMEViewer):

	handle = ["text/html"]

	def unquote(self, s):
		if len(s) > 2:
			if s[0] == "<" and s[-1] == ">":
				return s[1:-1]
		return s

	def toHTML(self):
		maindoc = None
		inline = {}
		for i in range(len(self.msg.parts)):
			p = self.msg.parts[i]
			p.unique_num = self.msg.unique_num
			p.path = self.msg.path + [i]
			cid = p.getheader("Content-Id", None)
			if cid: inline[self.unquote(cid)] = path2pid(p.path)
			ctype = p.gettype()
			if hasMIMEViewer(ctype):
				if not maindoc or ctype in self.handle:
					maindoc = p
		if maindoc:
			body = getBody(maindoc, self.kws)
			for key, value in inline.items():
				body = replace(body, "cid:%s" % key, "GetPart?index:int=%s&num=%s" % (
					self.msg.unique_num, value))
			return body
		else:
			return MultiViewer(self.msg)


class MessageViewer(MIMEViewer):

	def toHTML(self):
		html = HTMLFile(message_template)
		if self.msg.gettype() == "message/rfc822":
			path = self.msg.path
			un = self.msg.unique_num
			self.msg = Message(StringIO(self.msg.decode()))
			self.msg.unique_num = un
			self.msg.path = path
		return html(msg=self.msg, body=getBody(self.msg, self.kws))


urlpat = re.compile(r'(http|ftp|gopher)://[^>)\s]+')
emailpat = re.compile(r'(mailto:)?[-+,.\w]+@[-+.\w]+')

class TextViewer(MIMEViewer):

    def toHTML(self):
		def translate_email(match):
			return '<a href="Compose?To=%s">%s</a>' % \
				   (urlquote(match.group(0)),
					escape(match.group(0)))
		def translate_url(match):
			return '<a href="Goto?%s" target="_blank">%s</a>' % \
				   (urlquote(match.group(0)), escape(match.group(0)))
	
		html = HTMLFile(text_template)
		lines = split(self.msg.decode(), "\n")
		for i in xrange(len(lines)):
			start, links, l = 0, {}, escape(lines[i], 1)
			l=emailpat.sub(translate_email, l)
			l=urlpat.sub(translate_url, l)                          
			if len(l) > 1 and lines[i][0] in [">", ":", "|"]:
				lines[i] = '<i><font color="darkblue">%s</font></i>' % l
			else: lines[i] = l
		return html(text=join(lines, "<br>\n"))


#XXX: handle frames and style-sheets somehow
class HTMLMailParser(SGMLParser):

	def __init__(self, base):
		SGMLParser.__init__(self, verbose=0)
		self.base = base
		self.data = self.title = ""
		self.titlestart = self.stopsave = 0
		self.linkcolor = self.vlink = self.alink = ""
		self.background = self.bgcolor = self.fgcolor = ""

	def fixlink(self, link):
	    if link[:8] == "Compose?": return link
	    if self.base:
		link = urljoin(self.base, link)
	    link = "Goto?%s" % urlquote(link)
	    return link
	
	def tuple2str(self, attrs):
		r = ""
		for key, value in attrs:
			if key in ["src", "href", "background"]:
				if len(value) > 4 and lower(value[:4]) == "cid:":
					pass
				else: value = self.fixlink(value)
			r = '%s %s="%s"' % (r, key, value)
		return r
	
	def tuple2dict(self, attrs):
		dict = {}
		for key, value in attrs:
			dict[lower(key)] = value
		return dict

	def dict2tuple(self, attrs):
	    tup = []
	    for key, value in attrs.items():
		tup.append((key, value))
	    return tup
	
	def save(self, data):
		if not self.stopsave:
			self.data = self.data + data

	def handle_comment(self, comment): self.save("<!--%s-->" % comment)
	def handle_entityref(self, name): self.save("&%s;" % name)
	def handle_charref(self, name): self.save("&#%s;" % name)
	def handle_data(self, data):self.save(data)
	def do_meta(self, attrs): pass
	def start_head(self, attrs): pass
	def end_head(self): pass
	def start_html(self, attrs): pass
	def end_html(self): pass
	def start_frameset(self, attrs): pass
	def end_frameset(self): pass
	def do_frame(self, attrs): pass
	def start_title(self, attrs): self.titlestart = len(self.data)
	def end_title(self): self.title = self.data[self.titlestart:]

	def start_a(self, attrs):
		opts = self.tuple2dict(attrs)
		opts["target"] = "_blank"
		attrs = self.dict2tuple(opts)
		url = opts.get("href", None)
		if url:
			if lower(url[:7]) == "mailto:":
				opts["href"] = "Compose?To=%s" % (url[7:])
		html = "<a%s>" % self.tuple2str(self.dict2tuple(opts))
		if self.linkcolor:
			html = '%s<font color="%s">' % (html, self.linkcolor)
		self.save(html)

	def end_a(self):
		if self.linkcolor: self.save("</font>")
		self.save("</a>")

	def start_body(self, attrs):
		self.data = "" 
		opts = self.tuple2dict(attrs)
		self.background = opts.get("background", "")
		self.bgcolor = opts.get("bgcolor", "")
		self.fgcolor = opts.get("text", "")
		self.linkcolor = opts.get("link", "")
		self.vlink = opts.get("vlink", "")
		self.alink = opts.get("alink", "")
		
	def end_body(self): self.stopsave = 1

	def do_base(self, attrs):
		opts = self.tuple2dict(attrs)
		if opts.has_key("href"):
			self.base = opts["href"]

	def unknown_starttag(self, tag, attrs):
		html = "<%s%s>" % (tag, self.tuple2str(attrs))
		self.save(html)

	def unknown_endtag(self, tag):
		html = "</%s>" % tag
		self.save(html)


class HTMLViewer(MIMEViewer):

	def toHTML(self):
		parser = HTMLMailParser(self.msg.getheader("Content-Base", None))
		parser.feed(self.msg.decode())
		html = HTMLFile(html_template)
		return html(mail=parser)


#XXX: Fix this hack. -> rfc2426
# V-Cards are much more complex
class VCardViewer(MIMEViewer):

	def toHTML(self):
		from lib.Message import mime_decode
		class VCard:
			empty = ["title", "fn", "street", "zip", "city", "state", "country",
					 "tel;home", "tel;work", "tel;cell", "tel;fax", "tel;pager",
					 "email;internet", "url"]
			def __init__(self, vc={}):
				for x in self.empty:
					if not vc.has_key(x):
						vc[x] = ""
				self.__dict__ = vc
			
		data = self.msg.decode()
		try:
			lines = split(data, "\n")
			entries = {}
			for l in lines:
				f = find(l, ":")
				if l[:f][-17:] == ";quoted-printable":
					key, value = l[:f-17], mime_decode(l[f+1:] or "")
				else:
					key, value = l[:f], l[f+1:]
				entries[key] = value
			card = VCard(entries)
			card.street, card.city, card.state, card.zip, \
						 card.country = split(entries.get("adr", ""), ";")[2:]
			html = HTMLFile(vcard_template)
			return html(card=card)
		except:
			return MIMEViewer.toHTML(self) #_("<br>[ VCard could not be parsed ]<br>")


class ImageViewer(MIMEViewer):

	def toHTML(self):
		if hasattr(self, "inlineimages") and not self.inlineimages:
			return apply(MIMEViewer, (self.msg,), self.kws)
		html = HTMLFile(image_template)
		return html(
			index=self.msg.unique_num, num=path2pid(self.msg.path),
			folder=self.folder, filename=self.msg.filename)


mime_viewers = {
	"message/rfc822": MessageViewer,
	"message/delivery-status": TextViewer,
	"multipart/alternative": AlternativeViewer,
	"multipart/mixed": MultiViewer,
	"multipart/report": MultiViewer,
	"multipart/related": RelatedViewer,
	"multipart/digest": MultiViewer,
	"text/rfc822-headers": MessageViewer,
	"text/plain": TextViewer,
	"text/html": HTMLViewer,
	"text/x-vcard": VCardViewer,
	"image/jpeg": ImageViewer,
	"image/png": ImageViewer,
	"image/x-xpixmap": ImageViewer,
	"image/gif": ImageViewer,
    }

getMIMEViewer = mime_viewers.get
hasMIMEViewer = mime_viewers.has_key

def getBody(msg, kws):
	ctype = msg.gettype()
	MIMEViewerClass = getMIMEViewer(ctype, MIMEViewer)
	body = apply(MIMEViewerClass, (msg,), kws)
	return body.__str__()
