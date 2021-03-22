# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Unit tests for target_decisioning_engine.artifact_provider module"""
# pylint: disable=too-many-public-methods
import json
import unittest
import time
import urllib3

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock
try:
    from http.client import NOT_MODIFIED, OK
except ImportError:
    from httplib import NOT_MODIFIED, OK

from urllib3.exceptions import MaxRetryError
from urllib3.response import HTTPResponse
from target_decisioning_engine.artifact_provider import ArtifactProvider
from target_decisioning_engine.constants import MINIMUM_POLLING_INTERVAL
from target_decisioning_engine.constants import DEFAULT_POLLING_INTERVAL
from target_decisioning_engine.types.decisioning_config import DecisioningConfig
from target_decisioning_engine.events import ARTIFACT_DOWNLOAD_FAILED
from target_decisioning_engine.events import ARTIFACT_DOWNLOAD_SUCCEEDED
from target_python_sdk.tests.helpers import spy_decorator

ARTIFACT_URL = "http://my.artifact.com"


class TestArtifactProvider(unittest.TestCase):

    def setUp(self):
        self.default_config = DecisioningConfig("client123", "org999", artifact_location=ARTIFACT_URL,
                                                event_emitter=Mock())
        self.provider = None

    def tearDown(self):
        self.provider.stop_polling()

    def test_get_polling_interval_equals_zero(self):
        config = DecisioningConfig(None, None, polling_interval=0)
        self.provider = ArtifactProvider(config)

        with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()):
            self.provider.initialize()
            self.assertEqual(self.provider.polling_interval, 0)

    def test_get_polling_interval_below_minimum(self):
        config = DecisioningConfig(None, None, polling_interval=200)
        self.provider = ArtifactProvider(config)

        with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()):
            self.provider.initialize()
            self.assertEqual(self.provider.polling_interval, MINIMUM_POLLING_INTERVAL)

    def test_get_polling_interval_above_minimum(self):
        config = DecisioningConfig(None, None, polling_interval=350)
        self.provider = ArtifactProvider(config)

        with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()):
            self.provider.initialize()
            self.assertEqual(self.provider.polling_interval, 350)

    def test_get_polling_interval_not_numeric(self):
        config = DecisioningConfig(None, None, polling_interval="bad")
        self.provider = ArtifactProvider(config)

        with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()):
            self.provider.initialize()
            self.assertEqual(self.provider.polling_interval, DEFAULT_POLLING_INTERVAL)

    def test_polling_works(self):
        config = DecisioningConfig("client123", "org999", polling_interval=1, artifact_location=None)
        self.provider = ArtifactProvider(config)

        with patch.object(self.provider, "_get_polling_interval", return_value=1):
            with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()) as mock_http_call:
                self.provider.initialize()
                time.sleep(5)
                self.assertGreater(mock_http_call.call_count, 3)

    def test_artifact_location_from_config(self):
        config = DecisioningConfig("client123", "org999", polling_interval=350, artifact_location=ARTIFACT_URL)
        self.provider = ArtifactProvider(config)
        with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()) as mock_http_call:
            self.provider.initialize()
            expected_args = ("GET", ARTIFACT_URL)
            self.assertEqual(mock_http_call.call_count, 1)
            self.assertEqual(mock_http_call.call_args[0], expected_args)
            self.assertEqual(mock_http_call.call_args[1].get("headers"), {})
            self.assertEqual(self.provider.artifact_location, ARTIFACT_URL)
            self.assertTrue(self.provider.polling_timer.is_alive())

    def test_determine_artifact_location(self):
        config = DecisioningConfig("client123", "org999", polling_interval=350, artifact_location=None)

        self.provider = ArtifactProvider(config)
        with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()) as mock_http_call:
            self.provider.initialize()
            constructed_url = "https://assets.adobetarget.com/client123/production/v1/rules.json"
            expected_args = ("GET", constructed_url)
            self.assertEqual(mock_http_call.call_count, 1)
            self.assertEqual(mock_http_call.call_args[0], expected_args)
            self.assertEqual(mock_http_call.call_args[1].get("headers"), {})
            self.assertEqual(self.provider.artifact_location, constructed_url)
            self.assertTrue(self.provider.polling_timer.is_alive())

    def test_artifact_from_config(self):
        config = DecisioningConfig("client123", "org999", polling_interval=350, artifact_location=ARTIFACT_URL,
                                   artifact_payload={"a": 1, "b": 2})
        self.provider = ArtifactProvider(config)

        with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()) as mock_http_call:
            self.provider.initialize()
            mock_http_call.assert_not_called()
            self.assertEqual(self.provider.artifact_location, ARTIFACT_URL)
            self.assertEqual(self.provider.artifact, {"a": 1, "b": 2})
            self.assertTrue(self.provider.polling_timer.is_alive())

    def test_add_remove_subscription(self):
        self.provider = ArtifactProvider(self.default_config)

        # Test add_subscription
        subscriber = Mock()
        self.assertEqual(self.provider.subscription_count, 0)
        subscription_key = self.provider.subscribe(subscriber)
        self.assertEqual(self.provider.subscription_count, 1)
        self.assertEqual(self.provider.subscriptions.get(subscription_key), subscriber)

        response_data = {"y": 88, "q": 14}
        response_mock = Mock(status=OK, data=json.dumps(response_data))
        with patch.object(self.provider.pool_manager, "request", return_value=response_mock):
            self.provider.initialize()
            self.assertEqual(subscriber.call_count, 1)
            self.assertEqual(subscriber.call_args[0][0], response_data)

        # Test remove_subscription
        self.provider.unsubscribe(subscription_key)
        self.assertEqual(self.provider.subscription_count, 0)

    def test_remove_subscription_bad_key(self):
        self.provider = ArtifactProvider(self.default_config)
        self.assertEqual(self.provider.subscription_count, 0)
        self.provider.unsubscribe(100)
        self.assertEqual(self.provider.subscription_count, 0)

    def test_stop_all_polling(self):
        self.provider = ArtifactProvider(self.default_config)
        with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()):
            self.provider.initialize()  # starts polling thread
            self.assertTrue(self.provider.polling_timer.is_alive())
            self.assertFalse(self.provider.polling_halted)

            self.provider.stop_polling()
            self.assertIsNone(self.provider.polling_timer)
            self.assertTrue(self.provider.polling_halted)

    def test_resume_polling(self):
        self.provider = ArtifactProvider(self.default_config)
        with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()):
            self.provider.initialize()  # starts polling thread
            self.provider.stop_polling()
            self.assertTrue(self.provider.polling_halted)

            self.provider.resume_polling()
            self.assertTrue(self.provider.polling_timer.is_alive())
            self.assertFalse(self.provider.polling_halted)

    def test_fetch_artifact_request_with_last_response_etag(self):
        self.provider = ArtifactProvider(self.default_config)
        self.provider.last_response_etag = "123"
        with patch.object(self.provider.pool_manager, "request", return_value=HTTPResponse()) as mock_http_call:
            self.provider.initialize()
            expected_args = ("GET", ARTIFACT_URL)
            expected_headers = {
                "If-None-Match": "123"
            }
            self.assertEqual(mock_http_call.call_count, 1)
            self.assertEqual(mock_http_call.call_args[0], expected_args)
            self.assertEqual(mock_http_call.call_args[1].get("headers"), expected_headers)
            self.assertTrue(self.provider.polling_timer.is_alive())

    def test_fetch_artifact_request_with_retries(self):
        emitter_mock = Mock()
        config = DecisioningConfig("client123", "org999", artifact_location=ARTIFACT_URL, event_emitter=emitter_mock)
        with patch("target_decisioning_engine.artifact_provider.BACKOFF_FACTOR", 0):
            self.provider = ArtifactProvider(config)
            self.assertEqual(self.provider.http_retry.backoff_factor, 0)

        request_spy = spy_decorator(urllib3.connectionpool.HTTPConnectionPool.urlopen)
        with patch.object(urllib3.connectionpool.HTTPConnectionPool, 'urlopen', request_spy):
            self.provider.initialize()
            self.assertIsNone(self.provider.artifact)
            self.assertIsNone(self.provider.last_response_data)
            self.assertIsNone(self.provider.last_response_etag)
            self.assertTrue(self.provider.polling_timer.is_alive())
            self.assertEqual(request_spy.mock.call_count, 11)
            self.assertEqual(emitter_mock.call_count, 1)
            self.assertEqual(emitter_mock.call_args[0][0], ARTIFACT_DOWNLOAD_FAILED)
            self.assertTrue(isinstance(emitter_mock.call_args[0][1].get("error"), MaxRetryError))

    def test_fetch_artifact_response_status_not_modified(self):
        response_mock = Mock(status=NOT_MODIFIED)
        self.provider = ArtifactProvider(self.default_config)
        self.provider.last_response_data = {"z": 99}
        with patch.object(self.provider.pool_manager, "request", return_value=response_mock):
            self.provider.initialize()
            self.assertEqual(self.provider.last_response_data, {"z": 99})
            self.assertTrue(self.provider.polling_timer.is_alive())
            self.assertEqual(self.default_config.event_emitter.call_count, 0)

    def test_fetch_artifact_response_status_ok_with_etag(self):
        response_data = {"y": 88, "q": 14}
        response_headers = {
            "Etag": "12345"
        }
        response_mock = Mock(status=OK, data=json.dumps(response_data), headers=response_headers)
        self.provider = ArtifactProvider(self.default_config)
        with patch.object(self.provider.pool_manager, "request", return_value=response_mock):
            self.provider.initialize()
            self.assertEqual(self.provider.artifact, response_data)
            self.assertEqual(self.provider.last_response_data, response_data)
            self.assertEqual(self.provider.last_response_etag, "12345")
            self.assertTrue(self.provider.polling_timer.is_alive())
            self.assertEqual(self.default_config.event_emitter.call_args_list[0][0][0], ARTIFACT_DOWNLOAD_SUCCEEDED)
            self.assertEqual(self.default_config.event_emitter.call_args_list[0][0][1].get("artifact_location"),
                             self.default_config.artifact_location)
            self.assertEqual(self.default_config.event_emitter.call_args_list[0][0][1].get("artifact_payload"),
                             response_data)

    def test_fetch_artifact_response_status_ok_no_etag(self):
        response_data = {"y": 88, "q": 14}
        response_headers = {
            "Etag": None
        }
        response_mock = Mock(status=OK, data=json.dumps(response_data), headers=response_headers)
        self.provider = ArtifactProvider(self.default_config)
        with patch.object(self.provider.pool_manager, "request", return_value=response_mock):
            self.provider.initialize()
            self.assertEqual(self.provider.artifact, response_data)
            self.assertIsNone(self.provider.last_response_data)
            self.assertIsNone(self.provider.last_response_etag)
            self.assertTrue(self.provider.polling_timer.is_alive())
            self.assertEqual(self.default_config.event_emitter.call_args_list[0][0][0], ARTIFACT_DOWNLOAD_SUCCEEDED)
            self.assertEqual(self.default_config.event_emitter.call_args_list[0][0][1].get("artifact_location"),
                             self.default_config.artifact_location)
            self.assertEqual(self.default_config.event_emitter.call_args_list[0][0][1].get("artifact_payload"),
                             response_data)
