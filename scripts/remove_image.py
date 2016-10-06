#!/usr/bin/env python

import logging
import os
import sys
from argparse import ArgumentParser

import requests

DOCKYARD_ADDRESS = 'http://localhost'


def get_header(query, header):
    return requests.get('{}/v2/{}'.format(DOCKYARD_ADDRESS, query),
                        headers={'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}).headers[header]


def delete(query):
    return requests.delete('{}/v2/{}'.format(DOCKYARD_ADDRESS, query))


def parse_args():
    ap = ArgumentParser()
    ap.add_argument('image')
    return ap.parse_args()


def main():
    args = parse_args()
    image = args.image
    image_parts = image.split(':', 1)
    image_name = image_parts[0]
    image_tag = image_parts[1] if len(image_parts) > 1 else 'latest'
    try:
        digest = get_header('{}/manifests/{}'.format(image_name, image_tag), 'Docker-Content-Digest')
    except KeyError:
        logging.error('Could not find image {}.'.format(image))
        sys.exit(1)
    print('Removing image {}...'.format(image))
    deleted = delete('{}/manifests/{}'.format(image_name, digest))
    if deleted.status_code == 202:
        print('Removed.')
    else:
        logging.warn('There was a problem with removing image {}: {} {}.'.format(image, deleted, deleted.text))
    print('Running garbage collector...')
    sys.stdout.flush()
    sys.stderr.flush()
    os.system('/go/bin/registry garbage-collect /tmp/config.yml')


if __name__ == '__main__':
    main()
