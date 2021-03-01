# Copyright 2020 Adobe. All rights reserved.
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
try:
    from unittest.mock import patch, Mock, call
except ImportError:
    from mock import patch, Mock, call
from http.client import NOT_MODIFIED, OK
from urllib3.exceptions import SSLError
from target_decisioning_engine.artifact_provider import ArtifactProvider
from target_decisioning_engine.artifact_provider import HTTP_RETRY
from target_decisioning_engine.constants import MINIMUM_POLLING_INTERVAL
from target_decisioning_engine.constants import DEFAULT_POLLING_INTERVAL
from target_decisioning_engine.types.decisioning_config import DecisioningConfig
from target_decisioning_engine.events import ARTIFACT_DOWNLOAD_SUCCEEDED
from target_decisioning_engine.events import ARTIFACT_DOWNLOAD_FAILED
from target_decisioning_engine.events import GEO_LOCATION_UPDATED


class TestArtifactProvider(unittest.TestCase):

    def setUp(self):
        self.default_config = DecisioningConfig("client123", "org999")
        self.provider = ArtifactProvider(self.default_config)

    def tearDown(self):
        self.provider.stop_all_polling()

    def test_get_polling_interval_equals_zero(self):
        config = DecisioningConfig(None, None, polling_interval=0)
        self.provider = ArtifactProvider(config)
        result = self.provider.get_polling_interval()
        self.assertEqual(result, 0)

    def test_get_polling_interval_below_minimum(self):
        config = DecisioningConfig(None, None, polling_interval=200)
        self.provider = ArtifactProvider(config)
        result = self.provider.get_polling_interval()
        self.assertEqual(result, MINIMUM_POLLING_INTERVAL)

    def test_get_polling_interval_above_minimum(self):
        config = DecisioningConfig(None, None, polling_interval=350)
        self.provider = ArtifactProvider(config)
        result = self.provider.get_polling_interval()
        self.assertEqual(result, 350)

    def test_get_polling_interval_not_numeric(self):
        config = DecisioningConfig(None, None, polling_interval="bad")
        self.provider = ArtifactProvider(config)
        result = self.provider.get_polling_interval()
        self.assertEqual(result, DEFAULT_POLLING_INTERVAL)

    def test_initialize_artifact_location_not_string(self):
        config = DecisioningConfig("client123", "org999", polling_interval=350, artifact_location=None)

        with patch.object(ArtifactProvider, "fetch_artifact", return_value=None) as mock_fetch_artifact:
            self.provider = ArtifactProvider(config)
            self.provider.initialize()
            mock_fetch_artifact.assert_called_once()
            self.assertEqual(self.provider.artifact_location,
                             "https://assets.adobetarget.com/client123/production/v1/rules.json")
            self.assertTrue(self.provider.polling_timer.is_alive())

    def test_initialize_artifact_location_is_string(self):
        config = DecisioningConfig("client123", "org999", polling_interval=350, artifact_location="Mordor")
        with patch.object(ArtifactProvider, "fetch_artifact", return_value=None) as mock_fetch_artifact:
            self.provider = ArtifactProvider(config)
            self.provider.initialize()
            mock_fetch_artifact.assert_called_once()
            self.assertEqual(self.provider.artifact_location, "Mordor")
            self.assertTrue(self.provider.polling_timer.is_alive())

    def test_initialize_artifact_from_config(self):
        config = DecisioningConfig("client123", "org999", polling_interval=350, artifact_location="Mordor",
                                   artifact_payload={"a": 1, "b": 2})
        with patch.object(ArtifactProvider, "fetch_artifact", return_value=None) as mock_fetch_artifact:
            self.provider = ArtifactProvider(config)
            self.provider.initialize()
            mock_fetch_artifact.assert_not_called()
            self.assertEqual(self.provider.artifact_location, "Mordor")
            self.assertEqual(self.provider.artifact, {"a": 1, "b": 2})
            self.assertTrue(self.provider.polling_timer.is_alive())

    def test_add_remove_subscription(self):
        def subscriber():
            pass

        self.provider = ArtifactProvider(self.default_config)

        # Test add_subscription
        self.assertEqual(self.provider.subscription_count, 0)
        self.provider.add_subscription(subscriber)
        self.assertEqual(self.provider.subscription_count, 1)
        self.assertEqual(self.provider.subscriptions[1], subscriber)

        # Test remove_subscription
        self.provider.remove_subscription(1)
        self.assertEqual(self.provider.subscription_count, 0)

    def test_remove_subscription_bad_key(self):
        self.provider = ArtifactProvider(self.default_config)
        self.assertEqual(self.provider.subscription_count, 0)
        self.provider.remove_subscription(100)
        self.assertEqual(self.provider.subscription_count, 0)

    def test_emit_new_artifact(self):
        emitter = Mock()
        subscriber = Mock()
        config = DecisioningConfig("client123", "org999", event_emitter=emitter)
        self.provider = ArtifactProvider(config)
        self.provider.add_subscription(subscriber)
        self.assertEqual(self.provider.subscription_count, 1)

        payload = {"a": 1, "b": 2}
        self.provider.emit_new_artifact(payload)

        call1 = call(ARTIFACT_DOWNLOAD_SUCCEEDED, {
            "artifact_location": self.provider.artifact_location,
            "artifact_payload": payload
        })
        call2 = call(GEO_LOCATION_UPDATED, {
            "geo_context": {}
        })

        emitter.assert_has_calls([call1, call2], any_order=False)
        subscriber.assert_called_with(payload)

    def test_stop_all_polling(self):
        with patch.object(ArtifactProvider, "fetch_artifact", return_value=None):
            self.provider = ArtifactProvider(self.default_config)
            self.provider.initialize()  # starts polling thread
            self.assertTrue(self.provider.polling_timer.is_alive())

            self.provider.stop_all_polling()
            self.assertIsNone(self.provider.polling_timer)
            self.assertTrue(self.provider.polling_halted)

    def test_resume_polling(self):
        with patch.object(ArtifactProvider, "fetch_artifact", return_value=None):
            self.provider = ArtifactProvider(self.default_config)
            self.provider.initialize()  # starts polling thread
            self.provider.stop_all_polling()
            self.assertTrue(self.provider.polling_halted)

            self.provider.resume_polling()
            self.assertTrue(self.provider.polling_timer.is_alive())
            self.assertFalse(self.provider.polling_halted)

    def test_schedule_next_update_polling_halted(self):
        with patch.object(ArtifactProvider, "fetch_artifact", return_value=None):
            self.provider = ArtifactProvider(self.default_config)
            self.provider.initialize()  # starts polling thread
            self.assertTrue(self.provider.polling_timer.is_alive())
            self.assertFalse(self.provider.polling_halted)

            self.provider.stop_all_polling()
            self.provider.schedule_next_update()
            self.assertIsNone(self.provider.polling_timer)
            self.assertTrue(self.provider.polling_halted)

    def test_fetch_artifact_with_etag(self):
        artifact_url = "http://my.artifact.com"
        request_mock = Mock()
        self.provider = ArtifactProvider(self.default_config)
        self.provider.last_response_etag = "123"
        with patch("target_decisioning_engine.artifact_provider.http.request", request_mock):
            self.provider.fetch_artifact(artifact_url)
            expected_args = ("GET", "http://my.artifact.com")
            expected_kwargs = {
                "headers": {"If-None-Match": "123"},
                "retries": HTTP_RETRY
            }
            request_mock.assert_called_once_with(*expected_args, **expected_kwargs)

    def test_fetch_artifact_status_not_modified(self):
        artifact_url = "http://my.artifact.com"
        response_mock = Mock(status=NOT_MODIFIED)
        request_mock = Mock(return_value=response_mock)
        self.provider = ArtifactProvider(self.default_config)
        self.provider.last_response_data = {"z": 99}
        with patch("target_decisioning_engine.artifact_provider.http.request", request_mock):
            self.provider.fetch_artifact(artifact_url)
            self.assertEqual(self.provider.last_response_data, {"z": 99})

    def test_fetch_artifact_status_ok_with_etag(self):
        artifact_url = "http://my.artifact.com"
        response_data = {"y": 88, "q": 14}
        response_headers = {
            "Etag": "12345"
        }
        response_mock = Mock(status=OK, data=json.dumps(response_data), headers=response_headers)
        request_mock = Mock(return_value=response_mock)
        self.provider = ArtifactProvider(self.default_config)
        with patch("target_decisioning_engine.artifact_provider.http.request", request_mock):
            artifact = self.provider.fetch_artifact(artifact_url)
            self.assertEqual(artifact, response_data)
            self.assertEqual(self.provider.last_response_data, response_data)
            self.assertEqual(self.provider.last_response_etag, "12345")

    def test_fetch_artifact_status_ok_no_etag(self):
        artifact_url = "http://my.artifact.com"
        response_data = {"y": 88, "q": 14}
        response_headers = {
            "Etag": None
        }
        response_mock = Mock(status=OK, data=json.dumps(response_data), headers=response_headers)
        request_mock = Mock(return_value=response_mock)
        self.provider = ArtifactProvider(self.default_config)
        with patch("target_decisioning_engine.artifact_provider.http.request", request_mock):
            artifact = self.provider.fetch_artifact(artifact_url)
            self.assertEqual(artifact, response_data)
            self.assertIsNone(self.provider.last_response_data)
            self.assertIsNone(self.provider.last_response_etag)

    def test_fetch_artifact_status_other(self):
        artifact_url = "http://my.artifact.com"
        response_mock = Mock(status=999)
        request_mock = Mock(return_value=response_mock)
        self.provider = ArtifactProvider(self.default_config)
        with patch("target_decisioning_engine.artifact_provider.http.request", request_mock):
            artifact = self.provider.fetch_artifact(artifact_url)
            self.assertIsNone(artifact)
            self.assertIsNone(self.provider.last_response_data)
            self.assertIsNone(self.provider.last_response_etag)

    def test_fetch_artifact_exception(self):
        artifact_url = "http://my.artifact.com"
        request_mock = Mock()
        emitter = Mock()
        config = DecisioningConfig("client123", "org999", event_emitter=emitter)
        self.provider = ArtifactProvider(config)
        with patch("target_decisioning_engine.artifact_provider.http.request", request_mock):
            exception = SSLError("invalid certificate")
            request_mock.side_effect = exception
            self.provider.fetch_artifact(artifact_url)
            failure_event = {
                "artifact_location": artifact_url,
                "error": exception
            }
            event_args = (ARTIFACT_DOWNLOAD_FAILED, failure_event)
            emitter.assert_called_with(*event_args)
            self.assertIsNone(self.provider.last_response_data)
            self.assertIsNone(self.provider.last_response_etag)
