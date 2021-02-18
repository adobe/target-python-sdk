# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Test cases for utils.py"""
import unittest
from copy import deepcopy
from urllib3_mock import Responses
import delivery_api_client
from delivery_api_client import ChannelType
from target_python_sdk import TargetClient
from target_python_sdk.tests.delivery_api_mock import setup_mock
from target_python_sdk.tests.delivery_request_setup import create_delivery_request

from target_tools import utils

responses = Responses('requests.packages.urllib3')


class TestUtils(unittest.TestCase):

    @responses.activate
    def test_get_mbox_names(self):
        self.get_attributes_options = {
            'request': {
                'context': {'channel': ChannelType.WEB},
                'execute': {
                    'mboxes': [{'name': "one"}, {'name': "two"}]
                },
                'prefetch': {
                    'mboxes': [{'name': "three"}, {'name': "four"}]
                }
            }
        }

        client_options = {
            'client': "someClientId",
            'organization_id': "someOrgId"
        }

        self.client = TargetClient.create(client_options)

        setup_mock('get_attributes', responses)
        opts = deepcopy(self.get_attributes_options)
        opts['request'] = create_delivery_request(opts['request'])

        result = utils.get_mbox_names(opts['request'])
        self.assertTrue(isinstance(result, set))
        self.assertEqual(len(result), 4)
        self.assertTrue("one" in result)
        self.assertTrue("two" in result)
        self.assertTrue("three" in result)
        self.assertTrue("four" in result)

    @responses.activate
    def test_add_mboxes_to_request_adds_prefetch(self):
        self.get_attributes_options = {
            'request': {
                'context': {'channel': ChannelType.WEB},
                'prefetch': {
                    'mboxes': []
                }
            }
        }

        client_options = {
            'client': "someClientId",
            'organization_id': "someOrgId"
        }

        self.client = TargetClient.create(client_options)

        setup_mock('get_attributes', responses)
        opts = deepcopy(self.get_attributes_options)
        opts['request'] = create_delivery_request(opts['request'])

        self.assertDictContainsSubset(
            {
                'prefetch': {
                    'mboxes': [
                        {
                            'name': "mbox-foo",
                            'index': 1
                        },
                        {
                            'name': "mbox-bar",
                            'index': 2
                        },
                        {
                            'name': "mbox-baz",
                            'index': 3
                        }
                    ]
                }
            },
            utils.add_mboxes_to_request(
                ["mbox-foo", "mbox-bar", "mbox-baz"],
                opts['request'],
                "prefetch"
            )
        )

    @responses.activate
    def test_add_mboxes_to_request_adds_execute(self):
        self.get_attributes_options = {
            'request': {
                'context': {'channel': ChannelType.WEB},
                'execute': {
                    'mboxes': []
                }
            }
        }

        client_options = {
            'client': "someClientId",
            'organization_id': "someOrgId"
        }

        self.client = TargetClient.create(client_options)

        setup_mock('get_attributes', responses)
        opts = deepcopy(self.get_attributes_options)
        opts['request'] = create_delivery_request(opts['request'])

        self.assertDictContainsSubset(
            {
                'execute': {
                    'mboxes': [
                        {
                            'name': "mbox-foo",
                            'index': 1
                        },
                        {
                            'name': "mbox-bar",
                            'index': 2
                        },
                        {
                            'name': "mbox-baz",
                            'index': 3
                        }
                    ]
                }
            },
            utils.add_mboxes_to_request(
                ["mbox-foo", "mbox-bar", "mbox-baz"],
                opts['request'],
                "execute"
            )
        )

    @responses.activate
    def test_add_mboxes_to_request_adds_without_duplicates_preserves_existings(
            self):
        self.get_attributes_options = {
            'request': {
                'context': {'channel': ChannelType.WEB},
                'prefetch': {
                    'mboxes': [
                        {
                            'name': "mbox-foo",
                            'index': 6
                        },
                        {
                            'name': "mbox-jab",
                            'index': 2
                        }
                    ]
                }
            }
        }

        client_options = {
            'client': "someClientId",
            'organization_id': "someOrgId"
        }

        self.client = TargetClient.create(client_options)

        setup_mock('get_attributes', responses)
        opts = deepcopy(self.get_attributes_options)
        opts['request'] = create_delivery_request(opts['request'])

        self.assertDictContainsSubset(
            {
                'prefetch': {
                    'mboxes': [
                        {
                            'name': "mbox-foo",
                            'index': 6
                        },
                        {
                            'name': "mbox-jab",
                            'index': 2
                        },
                        {
                            'name': "mbox-bar",
                            'index': 7
                        },
                        {
                            'name': "mbox-baz",
                            'index': 8
                        }
                    ]
                }
            },
            utils.add_mboxes_to_request(
                ["mbox-foo", "mbox-bar", "mbox-baz"],
                opts['request'],
                "prefetch"
            )
        )
