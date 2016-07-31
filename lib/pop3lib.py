from util import StringIO
from poplib import *

CR = '\r'
LF = '\n'
CRLF = CR+LF

class POP3X(POP3):

	def _getlinebuf(self):
		line = self.file.readline()
		if not line: raise error_proto('-ERR EOF')
		if line[-2:] == CRLF: return line[:-2]
		if line[0] == CR: return line[1:-1]
		return line[:-1]

	def _longcmdbuf(self, line):
		self._putcmd(line)
		return self._getlongrespbuf()

	def _getlongrespbuf(self):
		resp = self._getresp()
		buf = StringIO(); bwrite = buf.write
		getline = self._getlinebuf
		line = getline()
		while line != '.':
			if line[:2] == '..':
				line = line[1:]
			bwrite(line); bwrite("\n")
			line = getline()
		buf.seek(0)
		return resp, buf, 0

	def retr(self, which):
		return self._longcmdbuf('RETR %s' % which)

	def top(self, which, howmuch):
		return self._longcmdbuf('TOP %s %s' % (which, howmuch))

