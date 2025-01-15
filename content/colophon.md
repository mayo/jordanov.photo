---
title: Colophon
template: page.html
extra:
  container_width: narrow
---
This site was created as an experiment after I downloaded my data from Flickr. I haven't posted anything new to Flickr in a really long time, since around the time it went downhill with Yahoo, and before it was picked up by SmugMug. I started posting my photos on my own site, and didn't really feel like going back to paying subscription and starting to upload to Flickr again. The magic was gone, so were lot of the people I used to follow, and the few groups that were still active changed enough that I wasn't enticed to go back. I didn't want to pay another subscription without much gain for me, and I don't like having ads served with my photos.

At first I didn't know what to do with the data – I had all the original photos, the only thing I'd be losing was the albums that were created on Flickr, groups, and comments. After while, was started getting curious about how hard it would be to re-publish the images under my own domain. Similar presentation to Flickr - Photostream, albums, individual photos with some metadata, but without re-creating Flickr. I didn't want a system to run, support, and maintain - just a static site hosting the images. That would mean no comments or groups, but I'm fine with that.

And so this experiment started... I took the base templates from my [own site][oyam.ca] and stuck with [Zola][zola]. For now, I'm keeping the tech setup the same as my site: building with [GitHub Actions][ga-actions], hosting on [Amazon S3][s3], and [CloudFlare][cf] for CDN.

I wrote some basic python code to ingest the JSON data and match it up to the photos, as the data export is really rudimentary and clearly does the bare minimum - the is no consistent way to match up the data to the photos. [Exiftool][et] is used to extract metadata from the photos.

In theory, it should be possible to add more photos fairly easily with this setup, but the site generation takes some minutes. If I were to ever start publishing here, I would probably look into different static site generators that can act on subset of files, or look into adding a new feature set to Zola.

I leave comments and groups for future exercise. Comments could be implemented via webmentions or simply posting on Mastodon/fediverse, and leaving it out of the basic site. Each photo could just be re-posted and link to the thread on there. I haven't really thought about groups, and how that experience could be re-created without creating a dynamic site. Perhaps something similar and de-coupled on fediverse?

The type face used on this site is [IBM Plex][ibm-plex] ([git][plex-git]).


[oyam.ca]: https://github.com/mayo/oyam.ca
[zola]: https://www.getzola.org
[ga-actions]: https://github.com/mayo/oyam.ca/actions
[s3]: http://aws.amazon.com/s3
[cf]: http://cloudflare.com
[et]: https://exiftool.org
[ibm-plex]: https://www.ibm.com/plex/
[plex-git]: https://github.com/IBM/plex
