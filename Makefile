.PHONY: po mo

po:
	xgettext -Lpython --output=messages.pot program.py libs/programclass/showplugins.py libs/programclass/authorization.py libs/programclass/showposts.py libs/uix/kv/activity/license.kv libs/uix/kv/activity/nawdrawer.kv libs/uix/kv/activity/baseclass/boxposts.py
	msgmerge --update --no-fuzzy-matching --backup=off data/locales/po/ru.po messages.pot
	msgmerge --update --no-fuzzy-matching --backup=off data/locales/po/en.po messages.pot

mo:
	mkdir -p data/locales/ru/LC_MESSAGES
	mkdir -p data/locales/en/LC_MESSAGES
	msgfmt -c -o data/locales/ru/LC_MESSAGES/langapp.mo data/locales/po/ru.po
	msgfmt -c -o data/locales/en/LC_MESSAGES/langapp.mo data/locales/po/en.po
