# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Test cases for TargetClient.send_notifications"""
import multiprocessing
import unittest
from copy import deepcopy

from urllib3_mock import Responses
from delivery_api_client import ChannelType
from target_python_sdk import TargetClient
from target_python_sdk.tests.delivery_api_mock import setup_mock
from target_python_sdk.tests.validation import validate_response
from target_python_sdk.tests.delivery_request_setup import create_delivery_request
from target_python_sdk.tests.helpers import get_client_options


responses = Responses('requests.packages.urllib3')


class TestSendNotifications(unittest.TestCase):

    def setUp(self):
        client_options = get_client_options()
        self.send_notifications_options = {
            'request': {
                'id': {
                    'tnt_id': '123'
                },
                'context': {
                    'channel': ChannelType.WEB
                },
                'notifications': [{
                    "id": "SummerOfferNotification",
                    "timestamp": 1611954531 * 1000,
                    "type": "display",
                    "mbox": {
                        "name": "SummerOffer"
                    },
                    "tokens": [
                        "GcvBXDhdJFNR9E9r1tgjfmqipfsIHvVzTQxHolz2IpSCnQ9Y9OaLL2gsdrWQTvE54PwSz67rmXWmSnkXpSSS2Q"
                    ]
                },
                    {
                        "id": "SummerShoesOfferNotification",
                        "timestamp": 1611954531 * 1000,
                        "type": "display",
                        "mbox": {
                            "name": "SummerShoesOffer"
                        },
                        "tokens": [
                            "GcvBXDhdJFNR9E9r1tgjfmqipfsIHvVzTQxHolz2IpSCnQ9Y9OaLL2gsdrWQTvE54PwSz67rmXWmSnkXpSSS2Q"
                        ]
                    }]
            }
        }
        self.client = TargetClient.create(client_options)

    def test_send_notifications_no_options(self):
        with self.assertRaises(Exception) as err:
            self.client.send_notifications({})
        self.assertEqual(str(err.exception), 'Options are required')

    def test_send_notifications_no_request(self):
        opts = {'request': {}}
        with self.assertRaises(Exception) as err:
            self.client.send_notifications(opts)
        self.assertEqual(str(err.exception), 'Request object of type DeliveryRequest is required')

    def test_send_notifications_invalid_notifications(self):
        request_opts = {
            'context': {
                'channel': 'web',
            },
            'notifications': []
        }

        opts = {
            'request': create_delivery_request(request_opts)
        }

        with self.assertRaises(Exception) as err:
            self.client.send_notifications(opts)
        self.assertEqual(str(err.exception), 'Notifications list is required in request')

    def test_send_notifications_invalid_callback(self):
        opts = deepcopy(self.send_notifications_options)
        opts['request'] = create_delivery_request(opts['request'])
        opts['callback'] = 'Should be a fn'
        with self.assertRaises(Exception) as err:
            self.client.send_notifications(opts)
        self.assertEqual(str(err.exception), 'Callback must be a callable function')

    @responses.activate
    def test_send_notifications_async(self):
        setup_mock('notifications', responses)

        shared = {'has_response': False}
        async_opts = deepcopy(self.send_notifications_options)
        async_opts['request'] = create_delivery_request(async_opts['request'])

        def verify_callback(result):
            self.assertEqual(len(responses.calls), 1)
            validate_response(self, result)
            shared['has_response'] = True

        async_opts['callback'] = verify_callback
        thread = self.client.send_notifications(async_opts)
        try:
            thread.get(timeout=5)  # Blocks current thread to keep test runner alive
        except multiprocessing.context.TimeoutError:
            self.fail("Test case timed out waiting for callback to be invoked")
        self.assertTrue(shared.get('has_response'))

    @responses.activate
    def test_send_notifications_sync(self):
        setup_mock('notifications', responses)
        opts = deepcopy(self.send_notifications_options)
        opts['request'] = create_delivery_request(opts['request'])

        result = self.client.send_notifications(opts)

        self.assertEqual(len(responses.calls), 1)
        # generated DeliveryResponse doesn't have notifications field, so no specific validation
        validate_response(self, result)
