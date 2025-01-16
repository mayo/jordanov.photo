---
title: Colophon
template: page.html
extra:
  container_width: narrow
---
This site is an experiment using my data from Flickr. I stopped posting to Flickr around the time it went downhill with Yahoo, and while I was excited SmugMug rescued it, I never really got back into it. I started posting my photos on my own site, and didn't really feel like going back to paying subscription; and it felt like the magic was gone - lot of the people and groups I interacted with were gone too.

I thoguht it would be a fun experiment to try to create something similar for single user, under own domain, and ideally without the need for lot of infrastructure and maintenance. Similar presentation to Flickr - Photostream, albums, individual photos with some metadata. I dodn't want a system to run, support, and maintain - just a static site hosting the images would do.

I took the base of my [own site][oyam.ca] including [Zola][zola]. To make things easier, I'm keeping the tech setup the same as my site: building with [GitHub Actions][ga-actions], hosting on [Amazon S3][s3], and [CloudFlare][cf] for CDN. I wrote couple of Python scripts to ingest images and generate the post files - see the site [git][site-git] repo. None of these services are required, though. Zola outputs a directory with html files, and so do the ingest tools, the files could be uploaded anywhere static html and image files can be served.

The ingest tools take the JSON data from Flickr does some work to match it up to the photo files (the data export is clearly the bare minimum - the is no consistent way to match up the data to the photos). [Exiftool][et] is used to extract metadata from the photos.

In theory, it should be possible to add more photos fairly easily with this setup, but the site generation takes some minutes. If I were to ever start publishing images frequently, I would probably look into different static site generators that can act on subset of files, or look into adding a new feature set to Zola.

The interactive features, like comments or groups, are left for for future exercise. Comments could be implemented via webmentions or simply posting on Mastodon/fediverse, and leaving it out of the basic site. I haven't really thought about groups, but a similar de-coupled approach could work.

The type face used on this site is [IBM Plex][ibm-plex] ([git][plex-git]). Icons are subset using [IcoMoon][icomoon] from [Linearicons][icons] and [Simple Icons][icons-brands].


[oyam.ca]: https://github.com/mayo/oyam.ca
[site-git]: https://github.com/mayo/jordanov.photo
[zola]: https://www.getzola.org
[ga-actions]: https://github.com/mayo/oyam.ca/actions
[s3]: http://aws.amazon.com/s3
[cf]: http://cloudflare.com
[et]: https://exiftool.org
[ibm-plex]: https://www.ibm.com/plex/
[plex-git]: https://github.com/IBM/plex
[icomoon]: https://icomoon.io
[icons]: https://linearicons.com
[icons-brands]: https://simpleicons.org
