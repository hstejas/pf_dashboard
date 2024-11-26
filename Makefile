.DEFAULT_GOAL := all

install:
	npm install
	npx parcel build js/*.js --dist-dir static/dist/ --public-url /static/dist/

clean:
	rm -fr node_modules
	rm -fr static/dist
	rm -fr .parcel-cache
	rm -f package-lock.json

all: install

.PHONY: all install clean
