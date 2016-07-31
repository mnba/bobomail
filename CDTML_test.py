class Test:
	"""Hallo <dtml-var name html_quote>!
	Na wie geht es dir?"""
	params = {"name": "Henning"}

	def __init__(self, Handler):
		self.Handler = Handler

	def __str__(self):
		self.template = self.Handler(self.__doc__)
		return apply(self.template, (), self.params)

	def __call__(self):
		if VERBOSE: print str(self)
		else: return str(self)

class Test2(Test):
	"""Zählen:
	  <dtml-in zahlen><dtml-var expr="_['sequence-index']+1"></dtml-in>
	"""
	params = {"zahlen": range(99)}

class Test3(Test):
	"""/etc/passwd:
	<dtml-in passwd><dtml-var sequence-index>
	  <dtml-var name> <dtml-var group> <dtml-var home> <dtml-var shell>
	</dtml-in>
	<dtml-var expr="_.len(passwd)"> entries
	"""
	class Entry:
		def __init__(self, line):
			self.name, self.password, self.uid, self.guid, self.group, \
					   self.home, self.shell = line

	import pwd
	passwd = []
	for p in pwd.getpwall():
		passwd.append(Entry(p))
	params = {"passwd": passwd}

class Test4(Test):
	"""
	<dtml-if a>a exists
	<dtml-else>a does not exist :-(
	</dtml-if>
	<dtml-if b>b exists
	<dtml-else>b does not exist :-(
	</dtml-if>
	<dtml-if expr="c<5">c < 5
    <dtml-else>c >= 5
	</dtml-if>
	"""
	params = {"b": 123, "c": 6}
	

from CDTML import CDTML
from time import time, clock

def bench(func, repeat=1, *args, **kws):
	start = time()
	for i in range(repeat):
		apply(func, args, kws)
	return time() - start
	
tests = [Test, Test2, Test3, Test4]
handler = [CDTML]
try:
	from DocumentTemplate import HTML
	handler.append(HTML)
except: print "ZTemplates not installed"

VERBOSE = 0
for t in tests:
	print t.__name__
	for h in handler:
		instance = t(h)
		result = bench(instance, repeat=2)
		print "%20.20f (%s)" % (result, h.__name__)
		#print "failed (%s)" % h
	print

