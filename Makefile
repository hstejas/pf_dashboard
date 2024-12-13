.DEFAULT_GOAL := all

init:
	npm install
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

install: clean
	npx parcel build js/*.js --dist-dir ./static/dist/ --public-url /static/dist/

clean:
	rm -fr static/dist

distclean: clean
	rm -fr .parcel-cache
	rm -fr node_modules
	rm -f package-lock.json
	rm -rf venv

all: install

watch: clean
	npx parcel watch js/*.js --dist-dir ./static/dist/ --public-url /static/dist/


.PHONY: all install clean distclean watch init
