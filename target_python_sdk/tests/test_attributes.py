# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Test cases for get_attributes"""
import unittest
from copy import deepcopy
from urllib3_mock import Responses
import delivery_api_client
from delivery_api_client import ChannelType
from target_python_sdk import TargetClient
from target_python_sdk.tests.delivery_api_mock import setup_mock
from target_python_sdk.tests.delivery_request_setup import create_delivery_request


responses = Responses('requests.packages.urllib3')

class TestGetAttributes(unittest.TestCase):

    @responses.activate
    def test_gets_attributes_from_api_response(self):
        self.get_attributes_options = {
            'request': {
                'id': {
                    'tnt_id': "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
                    'marketing_cloud_visitor_id': "07327024324407615852294135870030620007"
                },
                'context': {
                    'channel': ChannelType.WEB,
                    'mobile_platform': None,
                    'application': None,
                    'screen': None,
                    'window': None,
                    'browser': None,
                    'address': {
                        'url': "http://adobe.com",
                        'referring_url': None
                    },
                    'geo': None,
                    'time_offset_in_minutes': None,
                    'user_agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0",
                    'beacon': False
                },
                'prefetch': {
                    'mboxes': [
                        {
                            'name': "feature-flag-a",
                            'index': 1
                        }
                    ]
                },
                'execute': {
                    'mboxes': [
                        {
                            'index': 1,
                            'name': "feature-flag-b"
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

        feature_a = self.client.get_attributes(["feature-flag-a"], )

        self.assertEqual(feature_a.get_value(
            "feature-flag-a", "payment_experience"), "legacy")
        self.assertFalse(feature_a.get_value(
            "feature-flag-a", "show_feature_x"))
        self.assertEqual(feature_a.get_value(
            "feature-flag-a", "payment_gateway_version"), 2.3)
        self.assertEqual(feature_a.get_value(
            "feature-flag-a", "customer_feedback_value"), 10)

        self.assertDictEqual(feature_a.as_object("feature-flag-a"), {
            'payment_experience': "legacy",
            'show_feature_x': False,
            'payment_gateway_version': 2.3,
            'customer_feedback_value': 10
        })

        features = self.client.get_attributes(["feature-flag-a", "feature-flag-b"])

        self.assertEqual(features.get_value(
            "feature-flag-b", "purchase_experience"), "beta2")
        self.assertTrue(features.get_value("feature-flag-b", "show_feature_y"))
        self.assertEqual(features.get_value(
            "feature-flag-b", "cart_version"), 1.3)
        self.assertEqual(features.get_value(
            "feature-flag-b", "customer_survey_value"), 102)

        self.assertDictEqual(features.as_object("feature-flag-b"), {
            'purchase_experience': "beta2",
            'show_feature_y': True,
            'cart_version': 1.3,
            'customer_survey_value': 102
        })

    @responses.activate
    def test_fails_gracefully_if_an_attribute_does_not_exist(self):
        self.get_attributes_options = {
            'request': {
                'id': {
                    'tnt_id': "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
                    'marketing_cloud_visitor_id': "07327024324407615852294135870030620007"
                },
                'context': {
                    'channel': ChannelType.WEB,
                    'mobile_platform': None,
                    'application': None,
                    'screen': None,
                    'window': None,
                    'browser': None,
                    'address': {
                        'url': "http://adobe.com",
                        'referring_url': None
                    },
                    'geo': None,
                    'time_offset_in_minutes': None,
                    'user_agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0",
                    'beacon': False
                },
                'prefetch': {
                    'mboxes': [
                        {
                            'name': "feature-flag-a",
                            'index': 2
                        }
                    ]
                },
                'execute': {
                    'mboxes': [
                        {
                            'index': 2,
                            'name': "feature-flag-b"
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

        attributes = self.client.get_attributes(["unknown-flag"], opts)

        with self.assertRaises(Exception) as context:
            attributes.get_value("unknown-flag", "payment_experience")

        self.assertEqual(
            "Attribute 'payment_experience' does not exist for mbox 'unknown-flag'", str(context.exception))

    @responses.activate
    def test_adds_mbox_names_to_the_delivery_request_as_needed(self):
        self.get_attributes_options = {
            'request': {
                'id': {
                    'tnt_id': "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
                    'marketing_cloud_visitor_id': "07327024324407615852294135870030620007"
                },
                'context': {
                    'channel': ChannelType.WEB,
                    'mobile_platform': None,
                    'application': None,
                    'screen': None,
                    'window': None,
                    'browser': None,
                    'address': {
                        'url': "http://adobe.com",
                        'referring_url': None
                    },
                    'geo': None,
                    'time_offset_in_minutes': None,
                    'user_agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0",
                    'beacon': False
                },
                'prefetch': {
                    'mboxes': [
                        {
                            'name': "feature-flag-a",
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

        attributes = self.client.get_attributes(["feature-flag-b"], opts)

        self.assertTrue(attributes.get_value(
            "feature-flag-b", "show_feature_y"))

        self.assertDictEqual(attributes.as_object("feature-flag-b"), {
            'purchase_experience': "beta2",
            'show_feature_y': True,
            'cart_version': 1.3,
            'customer_survey_value': 102
        })
