# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for target_decisioning_engine.notification_provider module"""
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
import unittest
import time
from delivery_api_client import ChannelType
from delivery_api_client import MboxResponse
from delivery_api_client import Option
from delivery_api_client import OptionType
from delivery_api_client import VisitorId
from delivery_api_client import Metric
from delivery_api_client import MetricType
from target_python_sdk.utils import to_dict
from target_python_sdk.tests.delivery_request_setup import create_delivery_request
from target_decisioning_engine.notification_provider import NotificationProvider
from target_decisioning_engine.tests.helpers import expect_to_match_object


TARGET_REQUEST = create_delivery_request({
    "context": {
        "channel": ChannelType.WEB,
        "address": {
            "url": "http://local-target-test:8080/"
        },
        "userAgent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0"
    },
    "prefetch": {
        "mboxes": [
            {
                "name": "mbox-something",
                "index": 1
            }
        ]
    }
})
TARGET_REQUEST.id = VisitorId()


class TestNotificationProvider(unittest.TestCase):
    """TestNotificationProvider"""

    def setUp(self):
        self.mock_notify = Mock()
        self.provider = NotificationProvider(TARGET_REQUEST, None, self.mock_notify)

    def test_send_notifications_display_type(self):
        event_token = "B8C2FP2IuBgmeJcDfXHjGpNWHtnQtQrJfmRrQugEa2qCnQ9Y9OaLL2gsdrWQTvE54PwSz67rmXWmSnkXpSSS2Q=="
        options = [Option(content="<h1>it's firefox</h1>",
                          type=OptionType.HTML,
                          event_token=event_token)]
        mbox = MboxResponse(options=options, metrics=[], name="browser-mbox")
        self.provider.add_notification(mbox)

        self.provider.send_notifications()

        time.sleep(1)
        self.assertEqual(self.mock_notify.call_count, 1)
        self.assertEqual(len(self.mock_notify.call_args[0][0]["request"]["notifications"]), 1)
        received = to_dict(self.mock_notify.call_args[0][0]["request"]["notifications"][0])
        expected = {
            "id": "expect.any(String)",
            "impressionId": "expect.any(String)",
            "timestamp": "expect.any(Number)",
            "type": "display",
            "mbox": {
                "name": "browser-mbox"
            },
            "tokens": [
                "B8C2FP2IuBgmeJcDfXHjGpNWHtnQtQrJfmRrQugEa2qCnQ9Y9OaLL2gsdrWQTvE54PwSz67rmXWmSnkXpSSS2Q=="
            ]
        }
        expect_to_match_object(received, expected)

    def test_send_notifications_no_duplicates(self):
        event_token = "yYWdmhDasVXGPWlpX1TRZDSAQdPpz2XBromX4n+pX9jf5r+rP39VCIaiiZlXOAYq"
        content = [{
            "type": "insertAfter",
            "selector": "HTML > BODY > DIV:nth-of-type(1) > H1:nth-of-type(1)",
            "cssSelector": "HTML > BODY > DIV:nth-of-type(1) > H1:nth-of-type(1)",
            "content":
                '<p id="action_insert_15882850825432970">Better to remain silent and be thought a fool \
                    than to speak out and remove all doubt.</p>'
        }]
        options = [Option(content=content,
                          type=OptionType.ACTIONS,
                          event_token=event_token)]
        metrics = [Metric(type=MetricType.CLICK,
                          event_token="/GMYvcjhUsR6WVqQElppUw==",
                          selector="#action_insert_15882853393943012")]
        mbox = MboxResponse(options=options, metrics=metrics, name="target-global-mbox")
        self.provider.add_notification(mbox)
        self.provider.add_notification(mbox)  # duplicate

        self.provider.send_notifications()

        time.sleep(1)
        self.assertEqual(self.mock_notify.call_count, 1)
        self.assertEqual(len(self.mock_notify.call_args[0][0]["request"]["notifications"]), 1)
        received = to_dict(self.mock_notify.call_args[0][0]["request"]["notifications"][0])
        expected = {
            "id": "expect.any(String)",
            "impressionId": "expect.any(String)",
            "timestamp": "expect.any(Number)",
            "type": "display",
            "mbox": {
                "name": "target-global-mbox"
            },
            "tokens": [
                "yYWdmhDasVXGPWlpX1TRZDSAQdPpz2XBromX4n+pX9jf5r+rP39VCIaiiZlXOAYq"
            ]
        }
        expect_to_match_object(received, expected)

    def test_send_notifications_distinct_per_mbox(self):
        event_token = "yYWdmhDasVXGPWlpX1TRZDSAQdPpz2XBromX4n+pX9jf5r+rP39VCIaiiZlXOAYq"
        content = [{
            "type": "insertAfter",
            "selector": "HTML > BODY > DIV:nth-of-type(1) > H1:nth-of-type(1)",
            "cssSelector": "HTML > BODY > DIV:nth-of-type(1) > H1:nth-of-type(1)",
            "content":
                '<p id="action_insert_15882850825432970">Better to remain silent and be thought a fool \
                    than to speak out and remove all doubt.</p>'
        }]
        options = [Option(content=content,
                          type=OptionType.ACTIONS,
                          event_token=event_token)]
        metrics = [Metric(type=MetricType.CLICK,
                          event_token="/GMYvcjhUsR6WVqQElppUw==",
                          selector="#action_insert_15882853393943012")]
        mbox = MboxResponse(options=options, metrics=metrics, name="my-mbox")
        self.provider.add_notification(mbox)

        another_mbox = MboxResponse(options=options, metrics=metrics, name="another-mbox")
        self.provider.add_notification(another_mbox)

        self.provider.send_notifications()

        time.sleep(1)
        self.assertEqual(self.mock_notify.call_count, 1)
        self.assertEqual(len(self.mock_notify.call_args[0][0]["request"]["notifications"]), 2)
        first_received = to_dict(self.mock_notify.call_args[0][0]["request"]["notifications"][0])
        expected = {
            "id": "expect.any(String)",
            "impressionId": "expect.any(String)",
            "timestamp": "expect.any(Number)",
            "type": "display",
            "mbox": {},
            "tokens": [
                "yYWdmhDasVXGPWlpX1TRZDSAQdPpz2XBromX4n+pX9jf5r+rP39VCIaiiZlXOAYq"
            ]
        }
        first_expected = dict(expected)
        first_expected["mbox"]["name"] = "my-mbox"
        expect_to_match_object(first_received, first_expected)

        second_received = to_dict(self.mock_notify.call_args[0][0]["request"]["notifications"][1])
        second_expected = dict(expected)
        second_expected["mbox"]["name"] = "another-mbox"
        expect_to_match_object(second_received, second_expected)
