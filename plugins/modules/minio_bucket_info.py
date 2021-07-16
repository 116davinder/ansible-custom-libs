#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Davinder Pal <dpsangwal@gmail.com>

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
module: minio_bucket_info
short_description: Get Information about Minio Bucket.
description:
  - Get Information about Minio Bucket.
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
  list_buckets:
    description:
      - do you want to get list of available buckets?
    required: false
    type: bool
  get_bucket_versioning:
    description:
      - do you want to get bucket versioning for given I(bucket)?
    required: false
    type: bool
  get_bucket_replication:
    description:
      - do you want to get bucket replication for given I(bucket)?
    required: false
    type: bool
  get_bucket_lifecycle:
    description:
      - do you want to get bucket lifecycle for given I(bucket)?
    required: false
    type: bool
  get_bucket_tags:
    description:
      - do you want to get bucket tags for given I(bucket)?
    required: false
    type: bool
  get_bucket_policy:
    description:
      - do you want to get bucket policy for given I(bucket)?
    required: false
    type: bool
  get_bucket_notification:
    description:
      - do you want to get bucket notification for given I(bucket)?
    required: false
    type: bool
  get_bucket_encryption:
    description:
      - do you want to get bucket encryption for given I(bucket)?
    required: false
    type: bool
author:
  - "Davinder Pal (@116davinder) <dpsangwal@gmail.com>"
requirements:
  - minio
"""

EXAMPLES = """
- name: get list of sort buckets
  community.missing_collection.minio_bucket_info:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    list_buckets: true

- name: get version status of given bucket
  community.missing_collection.minio_bucket_info:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    get_bucket_versioning: true
    bucket: 'test'

- name: get replication status of given bucket
  community.missing_collection.minio_bucket_info:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    get_bucket_replication: true
    bucket: 'test'

- name: get lifecycle rules & their status of given bucket
  community.missing_collection.minio_bucket_info:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    get_bucket_lifecycle: true
    bucket: 'test'

- name: get tags of given bucket
  community.missing_collection.minio_bucket_info:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    get_bucket_tags: true
    bucket: 'test'

- name: get policy of given bucket
  community.missing_collection.minio_bucket_info:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    get_bucket_policy: true
    bucket: 'test'

- name: get notification details of given bucket
  community.missing_collection.minio_bucket_info:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    get_bucket_notification: true
    bucket: 'test'

- name: get encryption details of given bucket
  community.missing_collection.minio_bucket_info:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    get_bucket_encryption: true
    bucket: 'test'

- name: get encryption details of given bucket
  community.missing_collection.minio_bucket_info:
    endpoint: "localhost:9000"
    username: minioadmin
    password: minioadmin
    get_object_lock_config: true
    bucket: 'test'
"""

RETURN = """
buckets:
  description: list of buckets.
  returned: when `list_buckets` is defined and success.
  type: list
status:
  description: status of bucket versioning.
  returned: when `get_bucket_versioning` is defined and success.
  type: str
replication_rules:
  description: list of bucket replication rules.
  returned: when `get_bucket_replication` is defined and success.
  type: list
lifecycle_rules:
  description: list of bucket lifecycle rules.
  returned: when `get_bucket_lifecycle` is defined and success.
  type: list
tags:
  description: bucket tags.
  returned: when `get_bucket_tags` is defined and success.
  type: dict
policy:
  description: list of bucket policy.
  returned: when `get_bucket_policy` is defined and success.
  type: dict
notification:
  description: list of bucket notification.
  returned: when `get_bucket_notification` is defined and success.
  type: dict
encryption:
  description: status of bucket encryption.
  returned: when `get_encryption` is defined and success.
  type: dict
object_lock_config:
  description: status of bucket object locking.
  returned: when `get_object_lock_config` is defined and success.
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from minio import Minio
from minio.error import S3Error
import json


def _minio_bucket(client, module):
    try:
        _results = []
        if module.params['list_buckets']:
            buckets = client.list_buckets()
            return sorted([bucket.name for bucket in buckets])
        elif module.params['get_bucket_versioning']:
            return client.get_bucket_versioning(module.params['bucket']).status
        elif module.params['get_bucket_replication']:
            rules = client.get_bucket_replication(module.params['bucket'])
            if rules is not None:
                for rule in rules.rules:
                    _results.append({
                        "rule_id": rule.rule_id,
                        "status": rule.status
                    })
            return _results
        elif module.params['get_bucket_lifecycle']:
            rules = client.get_bucket_lifecycle(module.params['bucket'])
            if rules is not None:
                for rule in rules.rules:
                    _results.append({
                        "rule_id": rule.rule_id,
                        "status": rule.status
                    })
                return _results
        elif module.params['get_bucket_tags']:
            return client.get_bucket_tags(module.params['bucket'])
        elif module.params['get_bucket_policy']:
            return client.get_bucket_policy(module.params['bucket'])
        elif module.params['get_bucket_notification']:
            _res = client.get_bucket_notification(module.params['bucket'])
            return {
                "cloud_func_config_list": _res.cloud_func_config_list,
                "queue_config_list": _res.queue_config_list,
                "topic_config_list": _res.topic_config_list,
            }
        elif module.params['get_bucket_encryption']:
            _res = client.get_bucket_encryption(module.params['bucket'])
            if _res is not None:
                return {
                    "kms_id": _res.rule.kms_master_key_id,
                    "sse_algorithm": _res.rule.sse_algorithm,
                    "status": "enabled"
                }
            else:
                return {
                    "status": "disabled"
                }
        elif module.params['get_object_lock_config']:
            _res = client.get_object_lock_config(module.params['bucket'])
            if _res is not None:
                return {
                    "duration": _res.duration,
                    "mode": _res.mode
                }

    except S3Error as e:
        module.fail_json({"error_code": e.code, "error_message": e.message})


def main():
    argument_spec = dict(
        endpoint=dict(required=True),
        username=dict(required=True, aliases=['access_key']),
        password=dict(required=True, aliases=['secret_key']),
        secure=dict(required=False, type=bool, default=False),
        bucket=dict(required=False, type=str),
        list_buckets=dict(required=False, type=bool),
        get_bucket_versioning=dict(required=False, type=bool),
        get_bucket_replication=dict(required=False, type=bool),
        get_bucket_lifecycle=dict(required=False, type=bool),
        get_bucket_tags=dict(required=False, type=bool),
        get_bucket_policy=dict(required=False, type=bool),
        get_bucket_notification=dict(required=False, type=bool),
        get_bucket_encryption=dict(required=False, type=bool),
        get_object_lock_config=dict(required=False, type=bool),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=(
            ('get_bucket_versioning', True, ['bucket']),
            ('get_bucket_replication', True, ['bucket']),
            ('get_bucket_lifecycle', True, ['bucket']),
            ('get_bucket_tags', True, ['bucket']),
            ('get_bucket_policy', True, ['bucket']),
            ('get_bucket_notification', True, ['bucket']),
            ('get_bucket_encryption', True, ['bucket']),
            ('get_object_lock_config', True, ['bucket']),
        ),
        mutually_exclusive=[
            (
                'list_buckets',
                'get_bucket_versioning',
                'get_bucket_replication',
                'get_bucket_lifecycle',
                'get_bucket_tags',
                'get_bucket_policy',
                'get_bucket_notification',
                'get_bucket_encryption',
                'get_object_lock_config'
            )
        ],
    )

    client = Minio(
        endpoint=module.params['endpoint'],
        access_key=module.params['username'],
        secret_key=module.params['password'],
        secure=module.params['secure']
    )

    response = _minio_bucket(client, module)
    if module.params['list_buckets']:
        module.exit_json(buckets=response)
    elif module.params['get_bucket_versioning']:
        module.exit_json(status=response)
    elif module.params['get_bucket_replication']:
        module.exit_json(replication_rules=response)
    elif module.params['get_bucket_lifecycle']:
        module.exit_json(lifecycle_rules=response)
    elif module.params['get_bucket_tags']:
        module.exit_json(tags=response)
    elif module.params['get_bucket_policy']:
        module.exit_json(policy=response)
    elif module.params['get_bucket_notification']:
        module.exit_json(notification=response)
    elif module.params['get_bucket_encryption']:
        module.exit_json(encryption=response)
    elif module.params['get_object_lock_config']:
        module.exit_json(object_lock_config=response)
    else:
        module.fail_json("unknown options are passed")


if __name__ == '__main__':
    main()
