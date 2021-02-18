# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Test cases for attributes_provider.py"""
import unittest
from copy import deepcopy
from urllib3_mock import Responses
import delivery_api_client
from delivery_api_client import ChannelType
from target_python_sdk import TargetClient
from target_python_sdk.tests.delivery_api_mock import setup_mock
from target_python_sdk.tests.delivery_request_setup import create_delivery_request
from target_tools.attributes_provider import AttributesProvider

responses = Responses('requests.packages.urllib3')

class TestAttributesProvider(unittest.TestCase):

    def setUp(self):
        client_options = {
            'client': "someClientId",
            'organization_id': "someOrgId"
        }
        self.get_attributes_options = {
            "request": {
                "request_id": "2e401dcc43ea437b8cb6d178d49303e2",
                "id": {
                    "tnt_id": "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
                    "marketing_cloud_visitor_id": "07327024324407615852294135870030620007"
                },
                "context": {
                    "channel": ChannelType.WEB,
                    "address": {
                        "url": "http://adobe.com"
                    },
                    "user_agent":
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0",
                    "beacon": False
                },
                "experience_cloud": {
                    "analytics": {
                        "supplemental_data_id": "37D04BA8ED0E2962-71B165AC17259331",
                        "logging": "server_side"
                    }
                },
                "prefetch": {
                    "mboxes": [
                        {
                            "index": 2,
                            "name": "feature-flag-a"
                        }
                    ]
                }
            }
        }
        self.client = TargetClient.create(client_options)
    

    @responses.activate
    def test_has_appropriate_method_calls(self):
        setup_mock('attributes_provider', responses)
        opts = deepcopy(self.get_attributes_options)
        opts['request'] = create_delivery_request(opts['request'])

        feature = AttributesProvider(opts['response'])

        self.assertTrue(callable(feature.get_value))
        self.assertTrue(callable(feature.as_object))
        self.assertTrue(callable(feature.to_json))
        self.assertTrue(callable(feature.get_response))

        self.assertDictEqual(feature.get_response(), result['response'])

    @responses.activate
    def test_gets_value_for_single_mbox(self):
        setup_mock('attributes_provider', responses)
        opts = deepcopy(self.get_attributes_options)
        opts['request'] = create_delivery_request(opts['request'])
        result = self.client.get_offers(opts)

        feature_a = AttributesProvider(opts['response'])

        self.assertEqual(
            feature_a.get_value(
                "feature-flag-a",
                "payment_experience"),
            "legacy")
        self.assertFalse(
            feature_a.get_value(
                "feature-flag-a",
                "show_feature_x"))
        self.assertEqual(
            feature_a.get_value(
                "feature-flag-a",
                "payment_gateway_version"),
            2.3)
        self.assertEqual(
            feature_a.get_value(
                "feature-flag-a",
                "customer_feedback_value"),
            10)

        feature_b = AttributesProvider(opts['response'])

        self.assertEqual(
            feature_b.get_value(
                "feature-flag-b",
                "purchase_experience"),
            "beta2")
        self.assertTrue(
            feature_b.get_value(
                "feature-flag-b",
                "show_feature_y"))
        self.assertEqual(
            feature_b.get_value(
                "feature-flag-b",
                "cart_version"),
            1.3)
        self.assertEqual(
            feature_b.get_value(
                "feature-flag-b",
                "customer_survey_value"),
            102)

    @responses.activate
    def test_gets_value_for_multiple_mboxes_at_once(self):
        setup_mock('attributes_provider', responses)
        opts = deepcopy(self.get_attributes_options)
        opts['request'] = create_delivery_request(opts['request'])
        features = AttributesProvider(opts['response'])

        self.assertEqual(
            features.get_value(
                "feature-flag-a",
                "payment_experience"),
            "legacy")
        self.assertFalse(
            features.get_value(
                "feature-flag-a",
                "show_feature_x"))
        self.assertEqual(
            features.get_value(
                "feature-flag-a",
                "payment_gateway_version"),
            2.3)
        self.assertEqual(
            features.get_value(
                "feature-flag-a",
                "customer_feedback_value"),
            10)

        self.assertEqual(
            features.get_value(
                "feature-flag-b",
                "purchase_experience"),
            "beta2")
        self.assertTrue(features.get_value("feature-flag-b", "show_feature_y"))
        self.assertEqual(
            features.get_value(
                "feature-flag-b",
                "cart_version"),
            1.3)
        self.assertEqual(
            features.get_value(
                "feature-flag-b",
                "customer_survey_value"),
            102)

    @responses.activate
    def test_gets_as_object(self):
        setup_mock('attributes_provider', responses)
        opts = deepcopy(self.get_attributes_options)
        opts['request'] = create_delivery_request(opts['request'])
        features = AttributesProvider(opts['response'])

        self.assertDictEqual(features.as_object("feature-flag-a"), {
            'payment_experience': "legacy",
            'show_feature_x': False,
            'payment_gateway_version': 2.3,
            'customer_feedback_value': 10
        })

        self.assertDictEqual(features.as_object("feature-flag-b"), {
            'purchase_experience': "beta2",
            'show_feature_y': True,
            'cart_version': 1.3,
            'customer_survey_value': 102
        })

        self.assertDictEqual(features.as_object(), {
            "feature-flag-a": {
                'payment_experience': "legacy",
                'show_feature_x': False,
                'payment_gateway_version': 2.3,
                'customer_feedback_value': 10
            },
            "feature-flag-b": {
                'purchase_experience': "beta2",
                'show_feature_y': True,
                'cart_version': 1.3,
                'customer_survey_value': 102
            }
        })

        self.assertDictEqual(features.to_json(), {
            "feature-flag-a": {
                'payment_experience': "legacy",
                'show_feature_x': False,
                'payment_gateway_version': 2.3,
                'customer_feedback_value': 10
            },
            "feature-flag-b": {
                'purchase_experience': "beta2",
                'show_feature_y': True,
                'cart_version': 1.3,
                'customer_survey_value': 102
            }
        })

    @responses.activate
    def test_throws_an_error_if_an_attribute_does_not_exist(self):
        setup_mock('attributes_provider', responses)
        opts = deepcopy(self.get_attributes_options)
        opts['request'] = create_delivery_request(opts['request'])
        features = AttributesProvider(opts['response'])

        with self.assertRaises(Exception) as context:
            features.get_value("feature-flag-a", "my_property_name")

        self.assertEqual(
            "Attribute 'my_property_name' does not exist for mbox 'feature-flag-a'", str(context.exception))

        with self.assertRaises(Exception) as context:
            features.get_value("feature-flag-xyz", "my_property_name")

        self.assertEqual(
            "Attribute 'my_property_name' does not exist for mbox 'feature-flag-xyz'", str(context.exception))
