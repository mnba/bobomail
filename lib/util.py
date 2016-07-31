# Some usefull functions for BoboMail
try: from cStringIO import StringIO
except: from StringIO import StringIO

from htmlentitydefs import entitydefs
import urllib, string


exitlist = []
def atexit(func):
	global exitlist
	exitlist.append(func)

def exitall():
	for func in exitlist:
		func()

import sys
if hasattr(sys, "exitfunc"): atexit(sys.exitfunc)	
sys.exitfunc = exitall

def getusername(user):
	if user.host == "localhost":
		try:
			import pwd
			return string.split(pwd.getpwnam(user.id)[4], ",")[0]
		except: pass
	return ""


def urlquote(s): return urllib.quote_plus(s, "")
def urlunquote(s): return urllib.unquote_plus(s)

def quotedtext(text):
	def quotedline(line):
		return "> %s" % line
	return string.join(map(quotedline, string.split(text, "\n")), "\n")


replace_char = {"\n": "<br>\n", "\t": "&nbsp;" * 4}
for key, value in entitydefs.items():
    replace_char[value] = "&%s;" % key


def escape(s, spaces=0):
	nbsp = entitydefs["nbsp"]
	last = ""
	new = StringIO()
	for char in s:
		if spaces and char == " " and last in [" ", nbsp]:
			char = nbsp
		new.write(replace_char.get(char, char))
		last = char
	newstr = new.getvalue()
	if spaces and newstr and newstr[0] == " ":
	    return "&nbsp;%s" % newstr[1:]
	return newstr


def path2pid(path):return string.join(map(str, path), ".")
def pid2path(pid): return map(int, string.split(pid, "."))



def bytesizestr(bytes):
	s = ""
	if bytes > 1024 * 1024:
		mb = bytes / (1024 * 1024)
		s = "%s MB" % mb
	elif bytes > 1024:
		kb = bytes / 1024
		s = "%s KB" % kb
	else:
		s = "%s" % bytes
	return s

					 
