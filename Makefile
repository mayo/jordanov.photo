ZOLA_CONTENT_DIR := content
ZOLA_STATIC_DIR := static

# GPG_KEYID := 50fec3a364b59bee734d0e9b56a3789ced4d2dd7

# # Generated at https://keyoxide.org/util/wkd. Z-Base-32 encoded SHA1 of "mayo@oyam.ca" (Primary key UID)
# KEYOXIDE_WKD_HANDLE := sjd3shepa5rmabd9ggran4dsd5fd4sec

ZOLA_BIN ?= zola
GPG_BIN ?= gpg

# Main targets

build: zola-build

serve: zola-serve

dist: update-submodules depends #update-pubkey

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

clean-flickr:
	rm content/photos/[^_]*.md
	rm static/media/photos/*
