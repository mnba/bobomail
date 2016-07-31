all: bobomail.mo

bobomail.pot:
	./pygettext.py -v -d bobomail ../*.py ../dtml/*.html

de.po: bobomail.pot de.pox
	msgmerge -v -o de.po de.pox bobomail.pot

es_ES.po: bobomail.pot es_ES.pox
	msgmerge -v -o es_ES.po es_ES.pox bobomail.pot

pt_BR.po: bobomail.pot pt_BR.pox
	msgmerge -v -o pt_BR.po pt_BR.pox bobomail.pot

fi.po: bobomail.pot fi.pox
	msgmerge -v -o fi.po fi.pox bobomail.pot

de.pox:
	cp de.po de.pox

es_ES.pox:
	cp es_ES.po es_ES.pox

pt_BR.pox:
	cp pt_BR.po pt_BR.pox

fi.pox:
	cp fi.po fi.pox

bobomail.mo: de.po es_ES.po pt_BR.po fi.po 
	msgfmt -vfo de_DE/LC_MESSAGES/bobomail.mo de.po
	msgfmt -vfo es_ES/LC_MESSAGES/bobomail.mo es_ES.po
	msgfmt -vfo pt_BR/LC_MESSAGES/bobomail.mo pt_BR.po
	msgfmt -vfo fi_FI/LC_MESSAGES/bobomail.mo fi.po
