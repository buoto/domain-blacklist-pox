install:
	cp blacklist.py pox/ext/
	cp handler.py pox/ext/
	cp blacklist.py pox/ext/
	cp domain-blacklist.py pox/ext/
	cp models.py pox/ext/

run:
	cd pox; ./pox.py web domain-blacklist log.level --DEBUG