#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Davinder Pal <dpsangwal@gmail.com>

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
module: aws_kinesisvideo_info
short_description: Get Information about Amazon Kinesis Video Streams.
description:
  - Get Information about Amazon Kinesis Video Streams.
  - U(https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_Operations_Amazon_Kinesis_Video_Streams.html)
version_added: 0.0.7
options:
  list_streams:
    description:
      - do you want to get list of streams?
    required: false
    type: bool
  list_signaling_channels:
    description:
      - do you want to get list of signaling_channels?
    required: false
    type: bool
author:
  - "Davinder Pal (@116davinder) <dpsangwal@gmail.com>"
extends_documentation_fragment:
  - amazon.aws.ec2
  - amazon.aws.aws
requirements:
  - boto3
  - botocore
"""

EXAMPLES = """
- name: "get list of streams"
  aws_kinesisvideo_info:
    list_streams: true

- name: "get list of signaling_channels"
  aws_kinesisvideo_info:
    list_signaling_channels: true
"""

RETURN = """
streams:
  description: list of streams.
  returned: when `list_streams` is defined and success.
  type: list
signaling_channels:
  description: list of signaling_channels.
  returned: when `list_signaling_channels` is defined and success.
  type: list
"""

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass    # Handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.community.missing_collection.plugins.module_utils.aws_response_parser import aws_response_list_parser


def _kinesisvideo(client, module):
    try:
        if module.params['list_streams']:
            if client.can_paginate('list_streams'):
                paginator = client.get_paginator('list_streams')
                return paginator.paginate(), True
            else:
                return client.list_streams(), False
        elif module.params['list_signaling_channels']:
            if client.can_paginate('list_signaling_channels'):
                paginator = client.get_paginator('list_signaling_channels')
                return paginator.paginate(), True
            else:
                return client.list_signaling_channels(), False
        else:
            return None, False
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to fetch Amazon Kinesis Video Streams details')


def main():
    argument_spec = dict(
        list_streams=dict(required=False, type=bool),
        list_signaling_channels=dict(required=False, type=bool),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_if=(),
        mutually_exclusive=[
            (
                'list_streams',
                'list_signaling_channels',
            )
        ],
    )

    client = module.client('kinesisvideo', retry_decorator=AWSRetry.exponential_backoff())
    it, paginate = _kinesisvideo(client, module)

    if module.params['list_streams']:
        module.exit_json(streams=aws_response_list_parser(paginate, it, 'StreamInfoList'))
    elif module.params['list_signaling_channels']:
        module.exit_json(signaling_channels=aws_response_list_parser(paginate, it, 'ChannelInfoList'))
    else:
        module.fail_json("unknown options are passed")


if __name__ == '__main__':
    main()
