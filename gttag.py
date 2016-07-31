""" GNU gettext for DocumentTemplates !
If you want to use _ for translating
patch name_match in dtml_class.search (file DT_HTML.py)
Otherwise you can use <dtml-gettext>Some text</dtml-gettext>
or better <dtml-gt>Some other text</dtml-gt>"""

from DocumentTemplate.DT_Util import *
from DocumentTemplate.DT_String import String

import fintl, os

class I18NTag:
	"""
	This tag-extension for Zope's DocumentTemplates provides
	i18n-facilities as known from GNU gettext
	"""

	name = "gettext"
	blockContinuations = ()

	def __init__(self, blocks):
		self.tname, self.args, self.section = blocks[0]
		
	def render(self, md):
		args = parse_params(self.args, domain=None, locale=None, language=None)
		domain = args.get("domain", None)
		locale = args.get("locale", None)
		lang = args.get("language", None)
		if domain and locale:
			fintl.bindtextdomain(domain, locale)
			fintl.textdomain(domain)
		elif domain or locale:
			raise KeyError, "DTML-gettext: You have to set both  - domain and locale."
		if lang:
			os.environ["LANGUAGE"] = lang
		return fintl.gettext(self.section())

	__call__ = render

class ITag(I18NTag): name = "gt"

String.commands["gettext"] = I18NTag
String.commands["gt"] = ITag

