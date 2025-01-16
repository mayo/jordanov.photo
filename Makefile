ZOLA_CONTENT_DIR := content
ZOLA_STATIC_DIR := static

ZOLA_BIN ?= zola
GPG_BIN ?= gpg

# Main targets

build: zola-build

serve: zola-serve

dist: update-submodules depends

zola-build: photo-section-index
	$(ZOLA_BIN) build -u '/'

zola-serve: dist photo-section-index
	$(ZOLA_BIN) serve -u '/'

photo-section-index:
	find content/photos -type d -mindepth 1 -exec cp content-templates/photo-dir-index.md \{\}/_index.md \;

# Depends

depends: copy-fonts copy-reset-css copy-microevent-js

.PHONY: depends

copy-reset-css:
	cp depends/the-new-css-reset/css/reset.css sass/media/css/reset.css

copy-fonts:
	mkdir -p static/media/fonts/linearicons/
	cp depends/Linearicons-subset-v1.0/fonts/* static/media/fonts/linearicons/

copy-microevent-js:
	cp depends/microevent.js/microevent.js static/media/js/microevent.js


# Tools

update-submodules:
	git submodule update --recursive --init
