# jordanov.photo

## Makefile

The `depends` target will update all necessary files in the Zola site layout. For now and for reasns(tm), those files are checked in seaprately, so Zola can be executed without make targets to make everything work. It would be wise to reconsider this strategy at later date.

## Build and Deployment

See [Colophon](content/colophon/index.md) for details about the website build and deployment process.

The infrastructure for website deployment (GitHub Actions secrets, AWS roles, S3 bucket setup, etc) is managed using OpenTofu via my infrastructure management repository.

## Fonts

To update the subset font, load up `depends/Linearicons-subset-v1.0/selection.json` to https://icomoon.io, add new glyphs, and export (make sure all glyphs are selected). Replace contents of `depends/Linearicons-subset-v1.0` with the generated font, and replace files in `static/media/fonts/linearicons/` with new files from `depends/Linearicons-subset-v1.0/fonts` (or use the `copy-fonts` make target).

## Albums

The use of Albums is overloaded here. There is an `albums` taxonomy as well as `albums` section. When publishing, the taxonomy takes precedence, but having the section can be used for additional metadata. When rendering the `albums` *taxonomy*, the `albums` *section* is checked if it contains a page with same name (slug) as the taxonomy term. If such file exists, the page will be augmented with the data from the page. In this way, it is possible to specify alternate title, cover photo, or add a blurb about the gallery (regular page content).

There is a special/reserved album name `Featured`. Any images that belong in this album will be featured on the main page.

## Ingest

The files generated with the ingest are case sensitive. When running ingest on a Mac, it may be necessary to use alternate volume with case sensitive filesystem or using a linux container/VM.
