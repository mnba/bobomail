"""
This is a simple web application framework.
Currently it only contains some classes and functions for session management
and relies on the great ZPublisher and DocumentTemplate packages.

It is used and developed for BoboMail but has a generic interface to
make things even easier for rapid web development.
"""

__version__ = "0.02"
__author__ = "Henning Schroeder"


# Standard modules
import string, os, sys, __main__
# From Zope
from DocumentTemplate import HTML
import ZPublisher

# Own module
from session import SessionManager, SessionExpired


class WebApp:
	"Base class for a web application"

	def __init__(self, session_manager, master_template="", name=""):
		self.session_manager = session_manager
		self.template = master_template
		self.name = name or self.__classs__.__name__
		pubmod = sys.modules[getattr(__main__, "PUBLISHED_MODULE", "__main__")]
		#pubmod.zpublisher_exception_hook = self.handleException # XXX #MA: opened comment back
		pubmod.bobo_application = self

	def __bobo_traverse__(self, REQUEST, session=None):
		print "-*- start bt() -*-"
		#raise ZPublisher.interfaces.UseTraversalDefault
		# Some magic ;-)
		# URLs without session-id will be redirected
		self.REQUEST = REQUEST # XXX not sure if this is good for pcgi&friends
		CGI = REQUEST["SCRIPT_NAME"]
		relativeURL = "%s%s" % (CGI, REQUEST["PATH_INFO"])
		absoluteURL = "%s%s" % (REQUEST["SERVER_URL"], relativeURL)
		stack = REQUEST['TraversalRequestNameStack']
		print "DBG bt() session=", session, " stack=", stack
		# session manager is not None!! 
		#print "DBG bt() self.session_manager=", self.session_manager 
		
		#
		if False:
		  pass
		if REQUEST.has_key("SESSION"):
		  print "DBG __bobo_tr chp01"
		  sess = REQUEST["SESSION"]
		#elif session=="index_html":
		#  print "DBG __bobo_tr chp02"
		#  return getattr(self, "index_html")
		else:
		  print "DBG __bobo_tr chp03"
		  print "DBG  create new session"
		  sess = self.createNewSession(REQUEST)
		  REQUEST["SESSION"] = sess
		  REQUEST["SESSION_URL"] = "%s/sid_%s" % (CGI, sess.id)
		  if stack:
		     method = stack[-1]
		     del stack[-1]
		  else:
		     method = "index_html"
		  return getattr(self, method)
		print "DBG bt() session=", session
		
		raise ZPublisher.interfaces.UseTraversalDefault
		#
		
		if session[:4] == "sid_":
			print "DBG __bobo_tr chp1"
			sid = session[4:]
			sess = self.loadSession(REQUEST, sid)
			REQUEST["SESSION"] = sess
			REQUEST["SESSION_URL"] = "%s/sid_%s" % (CGI, sid)
			if stack:
				method = stack[-1]
				del stack[-1]
			else:
				method = "index_html"
			return getattr(self, method)
		elif self.session_manager is None:
			print "DBG __bobo_tr chp2"
			return getattr(self, session or "index_html")
		else:
			print "DBG __bobo_tr chp3: create new session"
			sess = self.createNewSession(REQUEST)
			#-print "DBG sess=", sess
			URL = "%s/sid_%s/%s" % (CGI, sess.id, relativeURL[len(CGI):])
			print "DBG URL=", URL
			QS = REQUEST.get("QUERY_STRING", "")
			if QS:
			   URL = "%s?%s" % (URL, QS)
			#raise "Redirect", URL
			#raise Exception("Redirect "+str( URL))
			#raise ZPublisher.interfaces.UseTraversalDefault
			raise

	def handleException(self, parents, request, exc_info0, exc_info1, exc_info2):
		"This hook gets called when an exception occures while publishing"
		print "DBG!: handleException", parents, request, exc_info0, exc_info1, exc_info2
		err_msg = str(exc_info1)
		if exc_info0 == "Redirect":
			raise
		else:
			print "Content-type: text/html\n"
			try:
				import pydoc #XXX: short term fix
				pydoc.HTMLRepr.repr_str = pydoc.HTMLRepr.repr_string
				import cgitb
				cgitb.handler()
			except ImportError:
				print string.replace(err_msg, "Zope", self.name)

	def genHTML(self, REQUEST, template, extra={}, **exchange):
		#This is a simple wrapper around DocumentTemplates
		if self.template: page = open(self.template).read()
		else: page = "<html><head></head>%(body)s<body></body></html>"
		if type(template) != type(""):
			data = template.read()
			template.close()
			template = data
		for old, new in extra.items():
			template = string.replace(template, old, new)
		extra["%(body)s"] = template
		for old, new in extra.items():
			page = string.replace(page, old, new)
		exchange["cgi"] = REQUEST.get("SESSION_URL",
									  REQUEST.get("SCRIPT_NAME", ""))
		session = REQUEST.get("SESSION", None)
		if session and session.password: exchange["loggedin"] = 1
		html = HTML(page)
		return apply(html, (), exchange)

	def createNewSession(self, REQUEST):
		"""createNewSession() -> new_session_id
		Gets automatically called when a new session is needed"""
		sess = self.session_manager.new()
		sess.remote = REQUEST.get("REMOTE_ADDR", "")
		return sess

	def loadSession(self, REQUEST, id):
		"""Loads a already created session
		Overload it to implement a login-handler"""
		try:
			sess = self.session_manager.load(id)
			if sess.remote != REQUEST.get("REMOTE_ADDR", ""):
				raise SessionExpired()
		except SessionExpired:
			sess = self.createNewSession(REQUEST)
			raise "Redirect",  "%s/sid_%s/" % (REQUEST["SCRIPT_NAME"], sess.id)
		return sess


class WebApplet:

	def __init__(self, parent_instance):
		self.webapp = parent_instance
		self.genHTML = self.webapp.genHTML


