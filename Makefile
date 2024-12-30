.DEFAULT_GOAL := all

init:
	npm install
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

BASE_PATH=
export BASE_PATH
install: clean
	npx parcel build js/*.js --dist-dir ./static/dist/ --public-url ${BASE_PATH}/static/dist/

test:
	. venv/bin/activate && pytest

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

REMOTE = pf_dashboard
PUSH_IMAGE = 
VERSION := $(shell git log --format="%h" -1)
docker_build:
	podman build --pull=newer --tag "${REMOTE}:${VERSION}" .
ifdef PUSH_IMAGE
	podman push "${REMOTE}:${VERSION}"
endif
	@echo "Image - ${REMOTE}:${VERSION}"


.PHONY: all install clean distclean watch init test docker_build
