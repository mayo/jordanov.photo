#!/usr/bin/env python3

# date time original
# aperture value, exposure time, flash
# focal length
# lon, tat
# make, model, lens model

# Process
# Upload image with additional metadata like title and description
# Extract exif, checksum, ID
# Generate all necessary image sizes and drop in place
# Generate Zola file
# Genrate site (should not need to have image in place, hopefully.)
# Upload

import argparse
from dataclasses import dataclass, field, fields
from datetime import datetime
import hashlib
import logging
import os.path
import sys
from typing import Type, TypeVar

import base58
import exiftool
import frontmatter
from frontmatter.default_handlers import SafeDumper
import shortuuid

# Change how null gets represented. Zola doesn't like `null`
SafeDumper.add_representer(
    type(None), lambda dumper, value: dumper.represent_scalar("tag:yaml.org,2002:null", "")
)


T = TypeVar("T")

class ETTag:
    Group: str = None
    Name: str = None

    @classmethod
    def to_arg(cls, raw=False, group=True):
        return f"-{cls.to_tag(raw, group)}"

    @classmethod
    def to_tag(cls, raw=False, group=True):
        return f"{cls.Group + ":" if group and cls.Group else ''}{cls.Name or cls.__name__[0:-5]}{"#" if raw else ''}"


# @dataclass
# class DateTimeETTag(ETTag):
#     @classmethod
#     def parse(cls, data):
#         return datetime.strptime(data, "%Y-%m-%dT%H:%M:%S")

class MakeETTag(ETTag): Group = "EXIF"
class ModelETTag(ETTag): Group = "EXIF"
class LensIDETTag(ETTag): Group = "Composite"
class DateTimeOriginalETTag(ETTag): Group = "EXIF"
class GPSLatitudeETTag(ETTag): Group = "Composite"
class GPSLongitudeETTag(ETTag): Group = "Composite"

class ISOETTag(ETTag): Group = "EXIF"
class FNumberETTag(ETTag): Group = "EXIF"
class ExposureTimeETTag(ETTag): Group = "EXIF"
class FlashETTag(ETTag): Group = "EXIF"
class FocalLengthETTag(ETTag): Group = "EXIF"

# No Group to make it more generic. Eg. PNG images have ImageWidth in PNG, not FILE group.
class ImageWidthETTag(ETTag): pass
class ImageHeightETTag(ETTag): pass

@dataclass
class CameraMeta:
    make: str = field(default=None)
    model: str = field(default=None)
    lens: str = field(default=None)

    @classmethod
    def from_et_json(cls: Type[T], data: dict) -> T:
        make = data.get(MakeETTag.to_tag(), None)
        model = data.get(ModelETTag.to_tag(), None)

        if make and model and model.startswith(make + " "):
            model = model[len(make):].strip()

        return cls(
            make=make,
            model=model,
            lens=data.get(LensIDETTag.to_tag(), None),
        )

@dataclass
class ExposureMeta:
    iso: int = field(default=None)
    aperture: float = field(default=None)
    shutter_speed: str = field(default=None)
    flash: bool = field(default=None)
    focal_length: int = field(default=None)

    @classmethod
    def from_et_json(cls: Type[T], data: dict) -> T:
        flash = data.get(FlashETTag.to_tag(), None)
        if flash:
            flash = int(flash) & 1 != 0

        return cls(
            iso=data.get(ISOETTag.to_tag(), None),
            aperture=data.get(FNumberETTag.to_tag(), None),
            shutter_speed=data.get(ExposureTimeETTag.to_tag(), None),
            flash=flash,
            focal_length=data.get(FocalLengthETTag.to_tag(), None),
        )

@dataclass
class GpsMeta:
    latitude: float = field(default=None)
    longitude: float = field(default=None)
    altitude: float = field(default=None)

    @classmethod
    def from_et_json(cls: Type[T], data: dict) -> T:
        return cls(
            latitude=data.get(GPSLatitudeETTag.to_tag(), None),
            longitude=data.get(GPSLongitudeETTag.to_tag(), None),
        )

@dataclass
class PhotoMeta:
    title: str = field(default=None)
    date: str = field(default=datetime.now())
    date_taken: str = field(default=None)
    albums: set() = field(default_factory=set)
    tags: set() = field(default_factory=set)
    photo_file: str = field(default=None)
    image_data_bl2b: str = field(default=None)
    content: str = field(default='')
    photo_id: str = field(default_factory=shortuuid.uuid)

    image_width: int = field(default=0)
    image_height: int = field(default=0)

    gps: GpsMeta = field(default=None)
    camera: CameraMeta = field(default=None)
    exposure: ExposureMeta = field(default=None)

    def __post_init__(self):
        if isinstance(self.date_taken, str):
            try:
                self.date_taken = datetime.strptime(self.date_taken, "%Y-%m-%d %H:%M:%S")
            except:
                print(f"Could not parse date: {self.date_taken}")
                self.date_taken = None

        if isinstance(self.date, str):
            try:
                self.date = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S")
            except:
                print(f"Could not parse date: {self.date}")
                self.date = None

    @classmethod
    def from_et_json(cls: Type[T], data: dict) -> T:
        image_width_keys = [ key for key in data.keys() if key.endswith(ImageWidthETTag.to_tag()) ]
        image_width = None
        if len(image_width_keys) > 0:
            image_width = data.get(image_width_keys[0], None)

        image_height_keys = [ key for key in data.keys() if key.endswith(ImageHeightETTag.to_tag()) ]
        image_height = None
        if len(image_height_keys) > 0:
            image_height=data.get(image_height_keys[0], None)

        return cls(
            date_taken=data.get(DateTimeOriginalETTag.to_tag(), None),
            gps=GpsMeta.from_et_json(data),
            camera=CameraMeta.from_et_json(data),
            exposure=ExposureMeta.from_et_json(data),

            image_width=image_width,
            image_height=image_height,
        )

    def update(self, other):
        for field in fields(PhotoMeta):
            if not getattr(self, field.name) and getattr(other, field.name):
                setattr(self, field.name, getattr(other, field.name))


class Ingest:
    def __init__(self, content_dir, photo_dir, template_file, photo_path_prefix=None, logger=None):
        self.logger = logger

        if not os.path.isfile(template_file):
            raise RuntimeError("Can't find template file")

        self.template_file = template_file

        self.content_dir = content_dir
        self.photo_dir = photo_dir
        self.photo_path_prefix = photo_path_prefix

        self.init_exiftool()

    def init_exiftool(self):
        # -n is good that some numbers don't get interpreted, but others do...
        # The best of both worlds is probably not using -n, and appending # to tag names
        # that we want raw.
        self.et = exiftool.ExifTool(common_args=["-G", '-c', '%-.6f', '-d', '%Y-%m-%d %H:%M:%S'], logger=self.logger)

    def _ensure_running(self):
        if not self.et.running:
            self.et.run()

    def get_checksum(self, photo_file):
        self._ensure_running()

        photo_bin = self.et.execute(
            photo_file,
            '-all=',
            '-commonifd0=',
            '-o', '-',

            raw_bytes=True
        )

        photo_b2b = hashlib.blake2b(photo_bin, digest_size=20)
        checksum = base58.b58encode(photo_b2b.digest()).decode('utf-8')

        return checksum

    def get_metadata(self, photo_file, checksum=False):
        self._ensure_running()

        et_params = [
            photo_file,
            MakeETTag.to_arg(),
            ModelETTag.to_arg(),
            LensIDETTag.to_arg(),

            DateTimeOriginalETTag.to_arg(),

            GPSLatitudeETTag.to_arg(),
            GPSLongitudeETTag.to_arg(),

            ISOETTag.to_arg(),
            FNumberETTag.to_arg(),
            ExposureTimeETTag.to_arg(),
            FlashETTag.to_arg(raw=True),
            FocalLengthETTag.to_arg(raw=True),

            ImageWidthETTag.to_arg(),
            ImageHeightETTag.to_arg(),
        ]

        metadata = self.et.execute_json(*et_params)

        pm = PhotoMeta.from_et_json(metadata[0])

        if checksum:
            pm.image_data_bl2b = self.get_checksum(photo_file)

        return pm

    def ingest(self, photo_meta, photo_file, update_meta_from_file=True, post_only=False, dry_run=False):
        et_photo_meta = self.get_metadata(photo_file, checksum=True)

        if photo_meta and update_meta_from_file:
            photo_meta.update(et_photo_meta)

        if not photo_meta:
            photo_meta = et_photo_meta

        _, photo_file_ext = os.path.splitext(photo_file)

        # copy + rename photo file
        dest_photo_file = f"{photo_meta.image_data_bl2b}{photo_file_ext}"
        dest_photo_path = os.path.join(
            photo_meta.image_data_bl2b[:2],
            photo_meta.image_data_bl2b[2:4]
        )
        dest_photo = os.path.join(dest_photo_path, dest_photo_file)

        fs_photo_path = os.path.join(
            self.photo_dir,
            dest_photo_path
        )
        fs_photo = os.path.join(fs_photo_path, dest_photo_file)

        cmd_exec_fn = os.system

        if dry_run:
            cmd_exec_fn = print

        if not post_only:
            cmd_exec_fn(f'mkdir -p {fs_photo_path}')
            cmd_exec_fn(f'cp "{photo_file}" "{fs_photo}"')

        # update photo_meta
        photo_meta.photo_file = dest_photo

        template = Template(self.template_file)
        post = template.fill(photo_meta, self.photo_path_prefix)

        post_path = os.path.join(
            self.content_dir,
            datetime.strftime(photo_meta.date, "%Y"),
            datetime.strftime(photo_meta.date, "%m"),
        )
        post_file = f"{photo_meta.photo_id}.md"

        cmd_exec_fn(f'mkdir -p {post_path}')

        if dry_run:
            print(frontmatter.dumps(post, sort_keys=False, Dumper=SafeDumper))
        else:
            out_path = os.path.join(post_path, post_file)
            frontmatter.dump(post, out_path, sort_keys=False, Dumper=SafeDumper)
            print(out_path)

        return post


class Template:
    def __init__(self, template_file):
        if not os.path.isfile(template_file):
            raise RuntimeError("Incorrect template file path")

        self.template_file = template_file

    def fill(self, photo_meta: PhotoMeta, path_prefix=None) -> frontmatter.Post:
        template = frontmatter.load(self.template_file)

        template['title'] = photo_meta.title

        if path_prefix:
            template['path'] = os.path.join(path_prefix, photo_meta.photo_id)

        if photo_meta.date:
            template['date'] = datetime.strftime(photo_meta.date, "%Y-%m-%dT%H:%M:%S")

        if photo_meta.camera.make or photo_meta.camera.model:
            template['taxonomies']['cameras'] = ["{} {}".format(photo_meta.camera.make, photo_meta.camera.model)]

        if photo_meta.camera.lens:
            template['taxonomies']['lenses'] = [photo_meta.camera.lens]
        template['taxonomies']['tags'] = photo_meta.tags
        template['taxonomies']['albums'] = photo_meta.albums

        if photo_meta.date_taken:
            template['extra']['date_taken'] = datetime.strftime(photo_meta.date_taken, "%Y-%m-%dT%H:%M:%S")

        template['extra']['image_data_bl2b'] = photo_meta.image_data_bl2b
        template['extra']['photo_id'] = photo_meta.photo_id
        template['extra']['photo_file'] = photo_meta.photo_file

        template['extra']['camera']['make'] = photo_meta.camera.make
        template['extra']['camera']['model'] = photo_meta.camera.model
        template['extra']['camera']['lens'] = photo_meta.camera.lens

        template['extra']['exposure']['iso'] = photo_meta.exposure.iso
        template['extra']['exposure']['shutter_speed'] = photo_meta.exposure.shutter_speed
        template['extra']['exposure']['aperture'] = photo_meta.exposure.aperture
        template['extra']['exposure']['flash'] = photo_meta.exposure.flash
        template['extra']['exposure']['focal_length'] = photo_meta.exposure.focal_length

        template['extra']['gps']['latitude'] = photo_meta.gps.latitude
        template['extra']['gps']['longitude'] = photo_meta.gps.longitude
        template['extra']['gps']['altitude'] = photo_meta.gps.altitude

        sizes = (float(photo_meta.image_width), float(photo_meta.image_height))

        if min(sizes) != 0:
            ratio = max(sizes) / min(sizes)

            if photo_meta.image_width > photo_meta.image_height:
                multiplier = 1
                if ratio > 1.7:
                    multiplier = 2
                if ratio > 2.7:
                    multiplier = 3

                template['extra']['width_multiplier'] = multiplier
            else:
                multiplier = 1
                if ratio > 1.2:
                    multiplier = 2
                if ratio > 2:
                    multiplier = 3

                template['extra']['height_multiplier'] = multiplier
        else:
            print("zero size", photo_meta.photo_id)

        template.content = photo_meta.content

        return template

class IngestCLI():
    def __init__(self):
        self._init_arg_parser()

    def _init_arg_parser(self):
        self.arg_parser = argparse.ArgumentParser(
            description='Ingest photos'
        )

        ingest_args = self.arg_parser.add_argument_group("ingest")

        ingest_args.add_argument('-c', '--content-dir', help="Content Directory to write files into")
        ingest_args.add_argument('-p', '--photo-dir', help="Directory to write photo files into")
        ingest_args.add_argument('-t', '--template-file', help="Content Template file")
        ingest_args.add_argument('-n', '--dry-run', action="store_true", help="Don't write to filesystem")
        ingest_args.add_argument('--photo-path-prefix', default=None, help="Override photo path prefix")
        ingest_args.add_argument('--post-only', action="store_true", help="Generate posts only, no image processing")

    def parse_args(self, argv, validate=True):
        args = self.arg_parser.parse_args(argv[1:])

        if validate:
            self.validate_args(args)

        return args

    def validate_args(self, args):

        if not os.path.isfile(args.template_file):
            print("Template file doesn't exist")
            exit(1)

        if not os.path.isdir(args.content_dir):
            print("Content directory doesn't exist")
            exit(1)

def parse_args(argv, ingest_cli):
    grp_args = ingest_cli.arg_parser.add_argument_group("cli")
    grp_args.add_argument('photofile')

    args = ingest_cli.parse_args(argv)

    if not os.path.isfile(args.photofile):
        print("Photo file doesn't exist")
        exit(1)

    return args


def main(argv):
    #root = logging.getLogger()
    #root.setLevel(logging.DEBUG)
    #handler = logging.StreamHandler(sys.stdout)
    #handler.setLevel(logging.DEBUG)
    #root.addHandler(handler)

    ing_cli = IngestCLI()
    args = parse_args(argv, ing_cli)

    #ing = Ingest(args.content_dir, args.photo_dir, args.template_file, photo_path_prefix=args.photo_path_prefix, logger=root)
    ing = Ingest(args.content_dir, args.photo_dir, args.template_file, photo_path_prefix=args.photo_path_prefix)

    ing.ingest(None, args.photofile, post_only=args.post_only, dry_run=args.dry_run)

if __name__ == '__main__':
    main(sys.argv)
