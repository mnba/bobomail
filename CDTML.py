import sys,os; pathsplit, getmtime = os.path.split, os.path.getmtime
splitext = os.path.splitext; pathjoin = os.path.join
try: from cStringIO import StringIO
except: from StringIO import StringIO

from string import find, strip, split, join, replace

try: from fintl import gettext
except:
	def gettext(s): return s
from cgi import escape
from urllib import quote_plus


from UserDict import UserDict

class Namespace(UserDict):

	def __call__(self, s=None):
		if s: return gettext(s)
		else: return self.data
		
	def len(self, object):
		return len(object)

def with(namespace, object, remove=0):
	ot = type(object)
	dict = {}
	if ot == type({}) or \
	   ot == type(UserDict):
		dict = object
	elif hasattr(object, "__dict__"):
		dict = object.__dict__
	for key, value in dict.items():
		if remove: del namespace[key]
		else: namespace[key] = value
		
		
def endwith(namespace, object):
	with(namespace, object, remove=1)


import regex; from string import lower
ListType=type([]); ParseError = "Error while parsing attribute"
def parse_params(text,
                 result=None,
                 tag='',
                 unparmre=regex.compile(
                     '\([\0- ]*\([^\0- =\"]+\)\)'),
                 qunparmre=regex.compile(
                     '\([\0- ]*\("[^"]*"\)\)'),
                 parmre=regex.compile(
                     '\([\0- ]*\([^\0- =\"]+\)=\([^\0- =\"]+\)\)'),
                 qparmre=regex.compile(
                     '\([\0- ]*\([^\0- =\"]+\)="\([^"]*\)\"\)'),
                 **parms):
    result=result or {}
    if parmre.match(text) >= 0:
        name=lower(parmre.group(2))
        value=parmre.group(3)
        l=len(parmre.group(1))
    elif qparmre.match(text) >= 0:
        name=lower(qparmre.group(2))
        value=qparmre.group(3)
        l=len(qparmre.group(1))
    elif unparmre.match(text) >= 0:
        name=unparmre.group(2)
        l=len(unparmre.group(1))
        if result:
            if parms.has_key(name):
                if parms[name] is None: raise ParseError, (
                    'Attribute %s requires a value' % name, tag)
				
                result[name]=parms[name]
            else:
				raise ParseError, (
                'Invalid attribute name, "%s"' % name, tag)
        else:
            result[name] = '' #result['']=name  XXX ???
        return apply(parse_params,(text[l:],result),parms)
    elif qunparmre.match(text) >= 0:
        name=qunparmre.group(2)
        l=len(qunparmre.group(1))
        if result: raise ParseError, (
            'Invalid attribute name, "%s"' % name, tag)
        else: result['']=name
        return apply(parse_params,(text[l:],result),parms)
    else:
        if not text or not strip(text): return result
        raise ParseError, ('invalid parameter: "%s"' % text, tag)
    
    if parms and not parms.has_key(name):
        raise ParseError, (
            'Invalid attribute name, "%s"' % name, tag)

    if result.has_key(name):
        p=parms[name]
        if type(p) is not ListType or p:
            raise ParseError, (
                'Duplicate values for attribute "%s"' % name, tag)
            
    result[name]=value

    text=strip(text[l:])
    if text: return apply(parse_params,(text,result),parms)
    else: return result



class Token:
	def __init__(self, **kws):
		self.__dict__ = kws
	def __repr__(self): return "<%s>" % self.__class__.__name__ 


class TagToken(Token): pass
class DataToken(Token): pass


class Scanner:

	def __init__(self, cdtml):
		self.cdtml = cdtml

	def start(self):
		self.found = find(self.cdtml, "<dtml-")
		if self.found != -1:
			self.queue = [DataToken(data=self.cdtml[0:self.found])]
		else:
			self.queue = []
		
	def next(self):
		if len(self.queue):
			token = self.queue[0]
			del self.queue[0]
			return token
		elif self.found != -1:
			tag, data = self.scan_next()
			self.queue.append(data)
			return tag
		#elif self.end < len(self.cdtml):
		#	token = DataToken(data=self.cdtml[self.end:])
		#	self.end = len(self.cdtml)
		#	return token
		
	def scan_next(self):
		space = find(self.cdtml, " ", self.found)
		self.end = find(self.cdtml, ">", self.found)
		if (space < self.end) and (space != -1):
			tag = self.cdtml[self.found+1:space]
			args = self.cdtml[space+1:self.end]
		else:
			tag = self.cdtml[self.found+1:self.end]
			args = ""
		self.end = self.end + 1				
		token1 = TagToken(name=tag, args=args)
		foundstart = find(self.cdtml, "<dtml-", self.end)
		foundend = find(self.cdtml, "</dtml-", self.end)
		self.found = min(foundstart, foundend)
		if self.found == -1:
			self.found = max(foundstart, foundend)
		if self.found == -1:
			data = self.cdtml[self.end:]
		else:
			data = self.cdtml[self.end:self.found]
		token2 = DataToken(data=data)
		return token1, token2



import sgmllib,re 
sgmllib.interesting = re.compile('([&<]dtml-)|(</dtml-)')

class NewScanner(sgmllib.SGMLParser):

	def __init__(self):
		sgmllib.SGMLParser.__init__(self)
		self.tokens = []

	def unknown_starttag(self, tag, attrs):
		self.tokens.append(Token(name=tag, args=attrs))

	def unknown_endtag(self, tag):
		self.tokens.append(Token(name="/%s" % tag))

	def handle_data(self, data):
		self.tokens.append(DataToken(data=data))
	


class UnknownToRenderException:
	def __init__(self, tag): self.tag = tag
	def __str__(self):return self.tag.name

class UnknownAttributeException:
	def __init__(self, name): self.name = name
	def __str__(self): return self.name


class Tag:

	def __init__(self, token, parent):
		self.name = token.name
		self.parse(token.args)
		self.check()
		self.parent = parent
		self.nodes = []
		if parent:
			self.indention = self.parent.indention + 1
			self.parent.add(self)

	def parse(self, s):
		params = split(s, " ")
		self.params = {}
		self.mainarg = params[0]
		for p in params[1:]:
			if "=" in p:
				f = find(p, "=")
				key, value = p[:f], p[f+1:]
			else:
				key, value = p, ""
			self.params[key] = value
	
	def add(self, item):
		self.nodes.append(item)

	def indent(self, increase=0):
		return "\t" * (self.indention+increase)
		
	def __str__(self):
		raise UnknownToRenderException(self)

	def __repr__(self):
		return str(self)

	def descend(self):
		out = ""
		for x in self.nodes:
			line = str(x)
			if line:
				out = "%s\n%s" % (out, line)
		return out

	def check(self):
		for a in self.params.keys():
			if a and (a not in self.attributes):
				raise UnknownAttributeException(a)

	def var(self, v):
		return "_['%s']" % v
			
class NullTag(Tag):

	def __init__(self):
		self.nodes = []
		self.parent = None
		self.indention = 0
		
	def __str__(self):
		return self.descend()


class DataTag(Tag):
	
	def __init__(self, token, parent):
		self.data = token.data
		self.nodes = []
		self.parent = parent
		self.indention = 0
		self.parent.add(self)
		self.indention = parent.indention + 1
		
	def __str__(self):
		data = repr(self)
		if data:
			return "%sout('%s')" % (self.indent(), data)

	def __repr__(self):
		if self.data:
			lines = split(self.data, "\n")
			return join(lines, "\\n")
			#space_before = ((self.data[0] == " ") and " ") or ""
			#space_after = ((self.data[-1] == " ") and " ") or ""
			#lines = split(self.data, "\n")
			#data = join(map(strip, lines), "\\n")
			#return replace("%s%s%s" % (
			#	data, space_before, space_after), "'", "\\'")
		else:
			return ""

		
class VarTag(Tag):
	attributes = ["html_quote", "url_quote", "size", "null", "missing"]

	def parse(self,s):
		Tag.parse(self, s)
		if " " in s:
			s = s[list(s).index(" "):]
			self.params = parse_params(text=s, tag="dtml-var",
									   html_quote=1, url_quote=1, missing=1,
									   null="", size="")
		
	def __str__(self):
		if self.mainarg[:6] == 'expr="':
			mainarg = "eval(%s, _())" % self.mainarg[5:]
		elif self.mainarg[0] == '"':
			mainarg = "eval(%s, _()) " % self.mainarg
		else:
			if self.params.has_key("missing"):
				mainarg = "_.get('%s', '')" % self.mainarg
			else:
				mainarg = self.var(self.mainarg)
		if self.params.has_key("null"):
			mainarg = "%s or %s" % (mainarg, self.var(self.params["null"]))
		if self.params.has_key("size"):
			mainarg = "'%%.%ss' %% %s" % (self.params["size"], mainarg)
		if self.params.has_key("html_quote"):
			return "%sout(escape(%s))" % (self.indent(), mainarg)
		elif self.params.has_key("url_quote"):
			return "%sout(quote_plus(%s))" % (self.indent(), mainarg)
		else:
			return "%sout(%s)" % (self.indent(), mainarg)


class GettextTagException:
	def __str__(self): return "Between tags there is no text"

class GettextTag(Tag):

	def __str__(self):
		for node in self.nodes:
			if (not isinstance(node, DataTag)):
				raise GettextTagException
			return "%sout(_('%s'))" % (self.indent(), repr(node))


class IfTag(Tag):
	attributes = []

	def __str__(self):
		if self.mainarg[:6] == 'expr="':
			mainarg = "eval(%s, _())" % self.mainarg[5:]
		elif self.mainarg[0] == '"':
			mainarg = 'eval(%s, _())' % self.mainarg
		else:
			mainarg = "_.get('%s', None)" % self.mainarg
		if self.name == "dtml-unless":
			unless = "not "
		else: unless = ""
		return "%sif %s%s:%s" % (
			self.indent(), unless, mainarg, self.descend())


class ElseTag(Tag):
	attributes = []
	
	def __str__(self):
		return "%selse:%s" % (self.indent(), self.descend())


class InTag(Tag):
	attributes = ["start", "size", "previous", "next", "reverse", "sort"]
	
	def __str__(self):
		mainarg = self.var(self.mainarg)
		
		if self.params.has_key("start"):
			start = self.var(self.params["start"])
		else: start = 0
		
		if self.params.has_key("size"):
			size = self.var(self.params["size"])
			end = "%s+%s" % (start, size)
		else:
			end = "len(%s)" % mainarg
			size = 32768
			
		if self.params.has_key("previous"):
			previous = """
%(i2)s%(pssn)s = ((%(start)s - %(size)s < 0) and %(start)s) or %(start)s - %(size)s
%(i2)s%(pss)s = ((%(start)s - %(size)s < 0) and %(start)s) or %(size)s
""" % {"pssn": self.var("previous-sequence-start-number"),
	   "pss": self.var("previous-sequence-size"),
	   "start": start, "i2": self.indent(1), "size": size}
		else:
			previous = ""
			
		if self.params.has_key("next"):
			next = """
%(i2)s%(nssn)s = ((%(start)s + %(size)s < %(end)s) and %(start)s) or %(start)s + %(size)s
%(i2)s%(nss) = ((%(start)s - %(size)s < %(end)s) and %(start)s) or %(size)s
""" % {"nssn": self.var("next-sequence-start-number"),
	   "nss": self.var("next-sequence-size"),
	   "start": start, "i2": self.indent(1), "size": size, "end": end}
		else:
			next = ""

		if self.params.has_key("sort"):
			sort = "%s%s.sort()" % (self.indent(), mainarg)
		else: sort = ""
		if self.params.has_key("reverse"):
			if sort: sort = "%s\n" % sort
			reversed = "%s%s.reverse()" % (self.indent(), mainarg)
		else: reversed = ""

		return """%(sort)s%(reversed)s
%(i)sfor sequence_index in xrange(%(start)s, %(end)s):
%(i2)s_["sequence-item"] = %(sequence)s[sequence_index]
%(i2)s_["sequence-index"] = sequence_index%(previous)s%(next)s
%(i2)swith(_, %(sequence)s[sequence_index])%(descend)s
%(i2)sendwith(_, %(sequence)s)""" % { 
			"i": self.indent(), "i2": self.indent(1), "sequence": mainarg,
			"start": start, "end": end, "previous": previous, "next": next,
			"reversed": reversed, "sort": sort,
			"descend": self.descend()}


class WithTag(Tag):
	attributes = []
	
	def __str__(self):
		return """%(i)swith(_, %(w)s)
%(i)sif 1:
%(c)s
%(i)sendwith(_, %(w)s)""" % {
			"i": self.indent(), "c": self.descend(), "w": self.var(self.mainarg)
			}


tag_handler = {
	"dtml-var": VarTag,
	"dtml-gt": GettextTag,
	"dtml-if": IfTag,
	"dtml-else": ElseTag,
	"dtml-unless": IfTag,
	"dtml-in": InTag,
	"dtml-with": WithTag
	}


class UnbalancedTagsException:
	def __init__(self, found, expected):
		self.found = found
		self.expected = expected
	def __str__(self):
		return "%s <> %s" % (self.found, self.expected)



class Parser:

	single_tags = ["dtml-var"]
	special_single_tags = ["dtml-else"]
	code = """# Compiled DTML

from CDTML import with, endwith, Namespace
from CDTML import escape, quote_plus, gettext

def render(out=None, **namespace):
\tif len(namespace)==0: namespace = globals()
\tif out==None: out = namespace["out"]
\t_ = Namespace(namespace)
\t_["_"] = _
%s
"""

	def __init__(self, scanner):
		self.scanner = scanner

	def start(self):
		self.scanner.start()
		self.indention = 0
		self.tree = None
		self.stack = []
		
	def parse(self):
		token = self.scanner.next()
		tree = NullTag()
		while token:
			if isinstance(token, TagToken):
				if token.name in self.single_tags:
					handler = tag_handler.get(token.name, Tag)
					handler(token, tree)
				elif token.name in self.special_single_tags:
					handler = tag_handler.get(token.name, Tag)
					tree = handler(token, tree.parent)
					if token.name == "dtml-else":
						if self.stack[-1] not in ["dtml-if", "dtml-unless"]:
 							raise UnbalancedTagsException(self.stack[-1], "dtml-if or dtml-unless")

				else:
					if token.name[0] != "/":
						self.indention = self.indention + 1
						handler = tag_handler.get(token.name, Tag)
						tree = handler(token, tree)
						self.stack.append(token.name)
					else:
						self.indention = self.indention - 1
						tree = tree.parent
						pop = self.stack.pop()
						if pop <> token.name[1:]:
							raise UnbalancedTagsException(pop, token.name[1:])
						
	  		elif token != None:
				DataTag(token, tree)
			token = self.scanner.next()

		while tree.parent != None:
			tree = tree.parent
		self.tree = tree

	def dump(self, direct=0):
		if direct: 
			return self.code % self.tree + \
				   "\nrender()"
		else:
			return self.code % self.tree


class CDTML:

	def __init__(self, cdtml):
		s = Scanner(cdtml)
		p = Parser(s)
		p.start()
		p.parse()
		self.code = p.dump(direct=1)
		print self.code
		self.compiled = compile(self.code, "<cdtml>", "exec")

	def _handler(self, data):
		self.out.write(str(data))

	def __call__(self, **kws):
		self.out = StringIO()
		namespace = kws
		namespace["out"] = self._handler
		eval(self.compiled, namespace)
		return self.out.getvalue()


class CDTMLFile:
	
	def __init__(self, filename, force=0):
		path, file = pathsplit(filename)
		if path not in sys.path: sys.path.append(path)
		name, ext = splitext(file)
		if ext: ext = ext[1:]
		self.pymod = "%s_%s" % (name, ext)
		self.pyfile = pathjoin(path, "%s.py" % self.pymod)
		try: date = getmtime(self.pyfile)
		except OSError: date = 0 
		if getmtime(filename) > date or force:
			data = open(filename).read()
			s = Scanner(data)
			p = Parser(s)
			p.start()
			p.parse()
			self.code = p.dump()
			open(self.pyfile, "w").write(self.code)
		self.module = __import__(self.pymod, globals(), locals(), "")
		
	def _handler(self, data):
		self.out.write(str(data))
		
	def __call__(self, **kws):
		self.out = StringIO()
		apply(self.module.render, (self._handler,), kws)
		return self.out.getvalue()



if __name__ == "__main__":
	if len(sys.argv) == 2:
		arg = sys.argv[1]
		from glob import glob
		for filename in glob(arg):
			print "Compiling %s.." % filename,
			cdtml = CDTMLFile(filename, force=1)
			print "ok"
	else:
		from time import time
		dtml = open("/usr/local/bobomail/dtml/list.html").read()
		start = time()
		s = Scanner(dtml)
		s.start()
		t = s.next()
		while t:
			t = s.next()
		print time() - start
		start = time()
		s2 = NewScanner()
		s2.feed(dtml)
		print time() - start
