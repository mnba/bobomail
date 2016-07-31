"""This module extends Python's rfc822 and mimetools
and it handles everything which has to do with mime and messages (e.g. multipart mails)"""

try: import locale; locale.setlocale(locale.LC_ALL,"")
except: pass

from calendar import weekday

import multifile
multifile.OriginalMultiFile = multifile.MultiFile
class MultiFile(multifile.OriginalMultiFile):
	"""This is a modified MultiFile class which accepts bad mime messages without end-markers.
	If anyone know of bad side-effects please tell me!"""
	
	def seek(self, pos, whence=0):
		here = self.tell()
		if whence:
			if whence == 1:
				pos = pos + here
			elif whence == 2:
				if self.level > 0:
					pos = pos + self.lastpos
				else:
					raise Error, "can't use whence=2 yet"
		#XXX: skip error
		#if not 0 <= pos <= here or \
		#		self.level > 0 and pos > self.lastpos:
		#	raise Error, 'bad MultiFile.seek() call'
		self.fp.seek(pos + self.start)
		self.level = 0
		self.last = 0

	def readline(self):
		if self.level > 0:
			return ''
		line = self.fp.readline()
		# Real EOF?
		if not line:
			self.level = len(self.stack)
			self.last = (self.level > 0)
			if self.last:
				# XXX skip error 
				pass # : raise Error, 'sudden EOF in MultiFile.readline()'
			return ''
		#assert self.level == 0
		# Fast check to see if this is just data
		if self.is_data(line):
			return line
		else:
			# Ignore trailing whitespace on marker lines 
			k = len(line) - 1;
			while line[k] in string.whitespace:
				k = k - 1
			marker = line[:k+1]
		# No?  OK, try to match a boundary.
		# Return the line (unstripped) if we don't.
		for i in range(len(self.stack)):
			sep = self.stack[i]
			if marker == self.section_divider(sep):
				self.last = 0
				break
			elif marker == self.end_marker(sep):
				self.last = 1
				break
		else:
			return line
		# We only get here if we see a section divider or EOM line
		if self.seekable:
			self.lastpos = self.tell() - len(line)
		self.level = i+1
		# XXX skip error
		#if self.level > 1:
		#	raise Error,'Missing endmarker in MultiFile.readline()'
		return ''

multifile.MultiFile = MultiFile

import mimetools, mimify, re, base64, string, time, rfc822
from util import StringIO


# XXX: also seen: =us-ascii
mime_head_quopri = re.compile('=\\?iso-8859-[12]\\?q\\?([^? \t\n]+)\\?=', re.I)
mime_head_base64 = re.compile('=\\?iso-8859-[12]\\?b\\?([^? \t\n]+)\\?=', re.I)

def mime_decode(line, isBase64=0):
	"""minify.mime_decode cannnot handle base64 encoded headers - this function can :-)"""
	if isBase64: return base64.decodestring(line)
	else: return mimify.mime_decode(line)


### Sample code recently found:
##encodings = {'B':'Base64', 'Q':'QP'}
##test = re.compile(r'=[?]([^?]+)[?]([BQ])[?]([^?]+)[?]=')
##newwords = []
##for word in string.split(commentpart):
##    mob = test.match(word)
##    if mob:
##        (charset, encoding, body) = mob.groups()
##        (fout, fin) = popen2.popen2('recode %s/%s' % (charset,
##                                    encodings[encoding]))
##        fin.write(body+'\n')
##        fin.close()
##        newwords.append(fout.readline()[:-1])
##    else:
##        newwords.append(word)
##name = string.join(newwords, ' ')

	
def mime_decode_header(line):
        """ mimify.mime_decode_header only decodes quoted printable -
        this one also handles base64 encoded headers Decode a header line to 8bit."""
        newline = ''
        pos = 0
        while 1:
                res = mime_head_quopri.search(line, pos)
                if res is None:
                        res = mime_head_base64.search(line, pos)
                        if res is None: break
                        else: isBase64 = 1
                else: isBase64 = 0
                match = res.group(1)
                # convert underscores to spaces (before =XX conversion!)
                match = string.join(string.split(match, '_'), ' ')
                newline = newline + line[pos:res.start(0)] + mime_decode(match, isBase64)
                pos = res.end(0)
	return newline + line[pos:]
	


class Message(mimetools.Message):
    """A real MIME-message class :-)
    Handles multipart messages and 
    helps decoding parts as well as headers.
    Disadvantage: slow on long mails :-(
    """
    
    def __init__(self, fp, preview=0):
		mimetools.Message.__init__(self, fp)
		self.body = ""
		self.parts = []
		self.encoding = self.getencoding()
		self.boundary = self.getparam("boundary")
		disp = self.getheader("content-disposition") or ""
		# XXX: parsing of parameters should be REALLY improved...
		f = string.find(disp, 'filename=')
		if f <> -1:
			fn = disp[f+9:]
			if len(fn) and fn[0] == '"':
				self.filename = fn[1:string.find(fn, '"', 1)]
			else:
				f = string.find(fn, " ")
				if f == -1: f = len(fn)
				self.filename = fn[:f] 
		else:
			self.filename = self.getparam("name")
		self.parsed = 0
		if not preview: self.parse()

    def parse(self):
		if self.parsed: return
		self.rewindbody()
		if self.boundary:
			mf = MultiFile(self.fp)
			mf.push(self.boundary)
			while mf.next():
				self.parts.append(Message(mf))
			mf.pop()
		else:
			self.body = self.fp.read()
			self.parsed = 1

    def decode(self):
		if self.encoding in ['7bit', '8bit']:
			return self.body
		self.rewindbody()
		out = StringIO()
		mimetools.decode(StringIO(self.body), out, self.encoding)
		return out.getvalue() # XXX look if there an error occurs
            
    def getheader(self, name, default=None):
		header = mimetools.Message.getheader(self, name, default)
		if header:
			return mime_decode_header(header)

    def getaddr(self, name):
		name, addr = mimetools.Message.getaddr(self, name)
		if name: return mime_decode_header(name), addr
		else: return name, addr
            
    def getaddrlist(self, name):
		addrs = rfc822.AddressList(self.getheader(name)).addresslist
		for i in range(len(addrs)):
			name = addrs[i][0]
			if name: 
				addrs[i] = mime_decode_header(name), addrs[i][1]
		return addrs

    def getdate(self, name):
		try:
			(year, month, day, hour, minute, second, _a, _b, _c) = mimetools.Message.getdate(self, name)
			# Hopefully the Julian day and daylight savings time are of no interest
			return (year, month, day, hour, minute, second, weekday(year, month, day), 0, 0)
		except: pass
    
    def __getitem__(self, name):
        return self.getheader(name)
    
    def __str__(self):
		# (re)build the message
		# If you want to create MIME message just set all headers and part
		# and do a mimemsgdata = str(yourMessageObject)
        f = StringIO()
        f.write('%s\n' % string.join(
            map(mimify.mime_encode_header, self.headers), ''))
        if self.parts: # multipart message
            for p in self.parts:
                f.write('\n--%s\n' % self.boundary)
                f.write(str(p))
            f.write('\n--%s--\n' % self.boundary)
        else:
            f.write(self.body or "")
        return f.getvalue()


