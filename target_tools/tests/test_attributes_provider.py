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

from target_python_sdk.tests.delivery_response_setup import create_delivery_response
from target_tools.attributes_provider import AttributesProvider

DELIVERY_RESPONSE = create_delivery_response({
    "status": 200,
    "requestId": "2e401dcc43ea437b8cb6d178d49303e2",
    "id": {
        "tntId": "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
        "marketingCloudVisitorId": "07327024324407615852294135870030620007"
    },
    "client": "adobesummit2018",
    "edgeHost": "mboxedge28.tt.omtrdc.net",
    "prefetch": {
        "mboxes": [
            {
                "index": 1,
                "name": "feature-flag-a",
                "options": [
                    {
                        "type": "json",
                        "content": {
                            "payment_experience": "legacy",
                            "show_feature_x": False,
                            "payment_gateway_version": 2.3,
                            "customer_feedback_value": 10
                        },
                        "eventToken":
                            "8MDICvd7bsTPYn79fLBNQmqipfsIHvVzTQxHolz2IpSCnQ9Y9OaLL2gsdrWQTvE54PwSz67rmXWmSnkXpSSS2Q=="
                    }
                ]
            }
        ]
    },
    "execute": {
        "mboxes": [
            {
                "index": 1,
                "name": "feature-flag-b",
                "options": [
                    {
                        "type": "json",
                        "content": {
                            "purchase_experience": "beta2",
                            "show_feature_y": True,
                            "cart_version": 1.3,
                            "customer_survey_value": 102
                        }
                    }
                ]
            }
        ]
    }
})

GET_OFFERS_RESPONSE = {
    "response": DELIVERY_RESPONSE
}


class TestAttributesProvider(unittest.TestCase):

    def setUp(self):
        self.attributes_provider = AttributesProvider(GET_OFFERS_RESPONSE)

    def test_get_response(self):
        self.assertDictEqual(self.attributes_provider.get_response(), GET_OFFERS_RESPONSE)

    def test_get_value_single_mbox(self):
        feature_a = AttributesProvider(GET_OFFERS_RESPONSE)

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

        feature_b = AttributesProvider(GET_OFFERS_RESPONSE)

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

    def test_get_value_multiple_mboxes(self):
        self.assertEqual(
            self.attributes_provider.get_value(
                "feature-flag-a",
                "payment_experience"),
            "legacy")
        self.assertFalse(
            self.attributes_provider.get_value(
                "feature-flag-a",
                "show_feature_x"))
        self.assertEqual(
            self.attributes_provider.get_value(
                "feature-flag-a",
                "payment_gateway_version"),
            2.3)
        self.assertEqual(
            self.attributes_provider.get_value(
                "feature-flag-a",
                "customer_feedback_value"),
            10)

        self.assertEqual(
            self.attributes_provider.get_value(
                "feature-flag-b",
                "purchase_experience"),
            "beta2")
        self.assertTrue(self.attributes_provider.get_value("feature-flag-b", "show_feature_y"))
        self.assertEqual(
            self.attributes_provider.get_value(
                "feature-flag-b",
                "cart_version"),
            1.3)
        self.assertEqual(
            self.attributes_provider.get_value(
                "feature-flag-b",
                "customer_survey_value"),
            102)

    def test_get_value_attribute_does_not_exist(self):
        with self.assertRaises(Exception) as context:
            self.attributes_provider.get_value("feature-flag-a", "my_property_name")

        self.assertEqual(
            "Attribute 'my_property_name' does not exist for mbox 'feature-flag-a'", str(context.exception))

        with self.assertRaises(Exception) as context:
            self.attributes_provider.get_value("feature-flag-xyz", "my_property_name")

        self.assertEqual(
            "Attribute 'my_property_name' does not exist for mbox 'feature-flag-xyz'", str(context.exception))

    def test_as_object_with_mbox_name(self):
        self.assertDictEqual(self.attributes_provider.as_object("feature-flag-a"), {
            "payment_experience": "legacy",
            "show_feature_x": False,
            "payment_gateway_version": 2.3,
            "customer_feedback_value": 10
        })

        self.assertDictEqual(self.attributes_provider.as_object("feature-flag-b"), {
            "purchase_experience": "beta2",
            "show_feature_y": True,
            "cart_version": 1.3,
            "customer_survey_value": 102
        })

    def test_as_object_without_mbox_name(self):
        self.assertDictEqual(self.attributes_provider.as_object(), {
            "feature-flag-a": {
                "payment_experience": "legacy",
                "show_feature_x": False,
                "payment_gateway_version": 2.3,
                "customer_feedback_value": 10
            },
            "feature-flag-b": {
                "purchase_experience": "beta2",
                "show_feature_y": True,
                "cart_version": 1.3,
                "customer_survey_value": 102
            }
        })

        self.assertDictEqual(self.attributes_provider.as_object(), {
            "feature-flag-a": {
                "payment_experience": "legacy",
                "show_feature_x": False,
                "payment_gateway_version": 2.3,
                "customer_feedback_value": 10
            },
            "feature-flag-b": {
                "purchase_experience": "beta2",
                "show_feature_y": True,
                "cart_version": 1.3,
                "customer_survey_value": 102
            }
        })
