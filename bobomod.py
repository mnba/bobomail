"""This module provides a base class which every BoboMail webmodule has to inherit"""

from webapp import WebApplet
from main import i18n
import main

class BoboMailModule(WebApplet):

	def __init__(self, *args, **kws):
		apply(WebApplet.__init__, (self,)+args, kws)
		self.genHTML = self._genHTML
		self.bobomail = self.webapp
		self.error = self.bobomail.error
		self.authError = self.bobomail.authError

	def _genHTML(self, REQUEST, template, extra={}, **exchange):
		exchange["imagedir"] = main.image_dir
		return apply(self.webapp.genHTML, (REQUEST, template, extra), exchange)
