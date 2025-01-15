#!/usr/bin/env python3

from dataclasses import dataclass
import json
import os.path
import re
import sys
from typing import Type, TypeVar

import frontmatter
import ingest
import shortuuid

T = TypeVar("T")

@dataclass
class GpsMeta(ingest.GpsMeta):
    @classmethod
    def from_json(cls: Type[T], data: dict) -> T:
        if len(data) < 1:
            return None

        latitude = data[0].get('latitude', None)
        longitude = data[0].get('longitude', None)

        if latitude:
            latitude = float(latitude) / 1000000.0

        if longitude:
            longitude = float(longitude) / 1000000.0

        return cls(latitude=latitude, longitude=longitude)

@dataclass
class PhotoMeta(ingest.PhotoMeta):
    @classmethod
    def from_json(cls: Type[T], data: dict) -> T:
        photo_id = data.get('photopage')
        if photo_id:
            photo_id = shortuuid.uuid(photo_id.rstrip('/'))

        return cls(
            title=data.get("name", None),
            date=data.get("date_imported", None),
            date_taken=data.get("date_taken", None),
            albums=[ a['title'] for a in data.get('albums', []) ],
            tags=[ t['tag'] for t in data.get('tags', []) ],
            gps=GpsMeta.from_json(data.get('geo', [])),
            content=data.get('description', ''),
            photo_id=photo_id
        )



def parse_args(argv, ingest_cli):
    flickr_args = ingest_cli.arg_parser.add_argument_group("flickr")

    flickr_args.add_argument('-d', '--data', help="Flickr data")
    flickr_args.add_argument('-l', '--limit', type=int, default=0, help="Only process given number of files")

    args = ingest_cli.parse_args(argv)

    if not os.path.isdir(args.data):
        print("Flickr data directory doesn't exist")
        exit(1)

    return args

def get_dirs(path):
    root, dirs, _ = next(os.walk(path))
    meta = [ d for d in dirs if re.match(r".*_part[0-9]+", d) ]
    data = [ d for d in dirs if re.match(r"data-.*-[0-9]+", d) ]

    return root, meta, data

def process_photo_meta(root, meta_dirs):
    for meta_dir in meta_dirs:
        parent, _, files = next(os.walk(os.path.join(root, meta_dir)))

        # count = 0
        for meta_file in files:
            if not meta_file.startswith("photo_"):
                continue

            # if count > 10: return
            # count += 1
            metadata = json.load(open(os.path.join(parent, meta_file)))

            yield(meta_file, metadata)

def process_album_meta(root, meta_dirs):
    ALBUM_FILE = "albums.json"
    for meta_dir in meta_dirs:
        parent, _, files = next(os.walk(os.path.join(root, meta_dir)))

        if ALBUM_FILE in files:
            metadata = json.load(open(os.path.join(parent, ALBUM_FILE)))

            yield(metadata['albums'])

def make_file_index(root_dir, data_dirs):
    lookup_by_id = {}
    lookup_by_file = {}

    id_pat = re.compile(r"^([0-9]+)_(?:[0-9]+[a-f]|[a-f]+[0-9])[0-9a-z]*_o.[a-z]{3,4}$|^.*_([0-9]+)_o.[a-z]{3,4}$")

    for data_dir in data_dirs:
        path = os.path.join(root_dir, data_dir)

        for _, _, files in os.walk(path):
            for photo_f in files:
                m = id_pat.match(photo_f)
                photo_id = m.group(2) or m.group(1)

                lookup_by_id[photo_id] = os.path.join(path, photo_f)
                lookup_by_file[photo_f] = os.path.join(path, photo_f)

    return lookup_by_id, lookup_by_file

def slugify(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9 ]', '', slug)
    slug = re.sub(r' ', '-', slug)

    return slug

def main(argv):
    ing_cli = ingest.IngestCLI()
    args = parse_args(argv, ing_cli)

    root_dir, meta_dirs, data_dirs = get_dirs(args.data)
    photo_idx_id, photo_idx_file = make_file_index(root_dir, data_dirs)

    ing = ingest.Ingest(args.content_dir, args.photo_dir, args.template_file, photo_path_prefix=args.photo_path_prefix)

    photos = process_photo_meta(root_dir, meta_dirs)
    photo_posts = {}

    count = 0
    for meta_file, metadata in photos:
        if args.limit > 0 and count > args.limit: break
        count += 1

        print(meta_file)

        photo_id = metadata['id']
        photo_file = photo_idx_id.get(photo_id)

        if photo_file is None:
            print("Could not match photo by ID, falling back to filename match")

            orig_file = os.path.basename(metadata['original'])
            photo_file = photo_idx_file.get(orig_file)

            if photo_file is None:
                print("Could not match photo by filename", meta_file, orig_file)

        photo_meta = PhotoMeta.from_json(metadata)

        photo_post = ing.ingest(photo_meta, photo_file, post_only=args.post_only, dry_run=args.dry_run)
        photo_posts[photo_post['extra']['photo_id']] = photo_post

    albums = process_album_meta(root_dir, meta_dirs)

    for albums_metadata in albums:
        for album in albums_metadata:

            post = frontmatter.load('content-templates/album.md')
            post.content = album['description']
            post['title'] = album['title']
            post['extra']['album_id'] = shortuuid.uuid(album['url'].rstrip('/'))
            photo_id = shortuuid.uuid(album['cover_photo'].rstrip('/'))
            post['extra']['cover_photo_id'] = photo_id
            cover_photo = photo_posts.get(photo_id)
            post['extra']['cover_photo'] = cover_photo['extra']['photo_file'] if cover_photo else None

            slug = slugify(post['title'])
            # print(frontmatter.dumps(post, sort_keys=False))
            frontmatter.dump(post, f'content/albums/{slug}.md', sort_keys=False)



if __name__ == '__main__':
    main(sys.argv)
