#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Davinder Pal <dpsangwal@gmail.com>

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
module: minio_bucket
short_description: Create/Update/Delete Minio Buckets.
description:
  - Create/Update/Delete Minio Buckets.
  - U(https://docs.min.io/docs/python-client-api-reference.html)
version_added: 0.1.1
options:
  endpoint:
    description:
      - minio api endpoint.
    required: true
    type: str
  username:
    description:
      - minio api endpoint username.
    required: true
    type: str
    aliases: ['access_key']
  password:
    description:
      - minio api endpoint password.
    required: true
    type: str
    aliases: ['secret_key']
  secure:
    description:
      - do you want to enable https/tls connection?
    required: false
    type: bool
    default: false
  bucket:
    description:
      - name of the minio bucket.
    required: false
    type: str
  location:
    description:
      - location for bucket.
    required: false
    type: str
    default: None
  object_lock:
    description:
      - do you want to enable object locking?
    required: false
    type: bool
    default: false
  tags:
    description:
      - dictionary of tags.
      - It will overrite existing tags of given I(bucket).
    required: false
    type: dict
  make_bucket:
    description:
      - create a given I(bucket), I(object_lock), and I(location)?
    required: false
    type: bool
  remove_bucket:
    description:
      - do you want to delete a for given I(bucket)?
    required: false
    type: bool
  set_bucket_tags:
    description:
      - do you want add tags to a given I(bucket) and I(tags)?
    required: false
    type: bool
author:
  - "Davinder Pal (@116davinder) <dpsangwal@gmail.com>"
requirements:
  - minio
"""

EXAMPLES = """
- name: create bucket in minio
  community.missing_collection.minio_bucket:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    make_bucket: true
    bucket: "test12"
    object_lock: false

- name: remove given bucket
  community.missing_collection.minio_bucket:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    remove_bucket: true
    bucket: 'test5'

- name: set bucket tags
  community.missing_collection.minio_bucket:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    set_bucket_tags: true
    bucket: 'test12'
    tags:
      project: "ansible"
"""

RETURN = """
"""

from ansible.module_utils.basic import AnsibleModule
from minio import Minio
from minio.error import S3Error
import json
from minio.tagging import Tags


def _minio_bucket(client, module):
    try:
        _bucket_name = module.params['bucket']
        if module.params['make_bucket']:
            if not client.bucket_exists(_bucket_name):
                client.make_bucket(
                    _bucket_name,
                    module.params['location'],
                    object_lock=module.params['object_lock']
                )
                module.exit_json(changed=True)
            else:
                module.exit_json(changed=False, msg="bucket already exists")
        elif module.params['remove_bucket']:
            if client.bucket_exists(_bucket_name):
                client.remove_bucket(_bucket_name)
                module.exit_json(changed=True)
            else:
                module.exit_json(changed=False, msg="bucket doesn't exist")
        elif module.params['set_bucket_tags']:
            tags = Tags.new_bucket_tags()
            for k in module.params['tags']:
                tags[k] = module.params['tags'][k]
            client.set_bucket_tags(_bucket_name, tags)
            module.exit_json(changed=True)
        else:
            module.fail_json(msg="unknown parameters")
    except S3Error as e:
        module.fail_json({"error_code": e.code, "error_message": e.message})


def main():
    argument_spec = dict(
        endpoint=dict(required=True),
        username=dict(required=True, aliases=['access_key']),
        password=dict(required=True, aliases=['secret_key']),
        secure=dict(required=False, type=bool, default=False),
        bucket=dict(required=False, type=str),
        location=dict(required=False, type=str, default=None),
        object_lock=dict(required=False, type=bool, default=False),
        tags=dict(required=False, type=dict),
        make_bucket=dict(required=False, type=bool),
        remove_bucket=dict(required=False, type=bool),
        set_bucket_tags=dict(required=False, type=bool),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=(
            ('make_bucket', True, ['bucket']),
            ('remove_bucket', True, ['bucket']),
            ('set_bucket_tags', True, ['bucket', 'tags']),
        ),
        mutually_exclusive=[
            (
                'make_bucket',
                'remove_bucket',
                'set_bucket_tags',
            )
        ],
    )

    client = Minio(
        endpoint=module.params['endpoint'],
        access_key=module.params['username'],
        secret_key=module.params['password'],
        secure=module.params['secure']
    )

    _minio_bucket(client, module)


if __name__ == '__main__':
    main()
