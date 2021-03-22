# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for TargetDecisioningEngine"""
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
import unittest
import time
import json
import os
from copy import deepcopy

from urllib3 import PoolManager, HTTPResponse

from target_decisioning_engine import TargetDecisioningEngine
from target_decisioning_engine import SUPPORTED_ARTIFACT_MAJOR_VERSION
from target_decisioning_engine import MESSAGES
from target_decisioning_engine.types.decisioning_config import DecisioningConfig
from target_decisioning_engine.events import ARTIFACT_DOWNLOAD_FAILED
from target_decisioning_engine.types.target_delivery_request import TargetDeliveryRequest
from target_python_sdk.tests.delivery_request_setup import create_delivery_request
from target_python_sdk.tests.helpers import read_json_file

CURRENT_DIR = os.path.dirname(__file__)
ARTIFACT_BLANK = read_json_file(CURRENT_DIR, "schema/artifacts/TEST_ARTIFACT_BLANK.json")
ARTIFACT_UNSUPPORTED_VERSION = read_json_file(CURRENT_DIR, "schema/artifacts/TEST_ARTIFACT_UNSUPPORTED.json")

TARGET_REQUEST = create_delivery_request({
    "context": {
        "channel": "web",
        "address": {
            "url": "http://local-target-test:8080/"
        },
        "userAgent":
            "Mozilla/5.0 (Macintosh Intel Mac OS X 10.15 rv:73.0) Gecko/20100101 Firefox/73.0"
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

CONFIG = DecisioningConfig("clientId", "orgId", maximum_wait_ready=500)

MOCK_ARTIFACT_RESPONSE = HTTPResponse(status=200, body=json.dumps(ARTIFACT_BLANK))
MOCK_ARTIFACT_RESPONSE_BAD = HTTPResponse(status=500)
MOCK_ARTIFACT_RESPONSE_UNSUPPORTED_VERSION = HTTPResponse(status=200, body=json.dumps(ARTIFACT_UNSUPPORTED_VERSION))


class TestTargetDecisioningEngine(unittest.TestCase):

    def setUp(self):
        self.decisioning = None

    def tearDown(self):
        if self.decisioning:
            self.decisioning.stop_polling()

    def test_initialize(self):
        config = deepcopy(CONFIG)
        config.polling_interval = 0
        self.decisioning = TargetDecisioningEngine(config)

        with patch.object(PoolManager, "request", return_value=MOCK_ARTIFACT_RESPONSE):
            self.decisioning.initialize()

        self.assertEqual(self.decisioning.artifact, ARTIFACT_BLANK)
        self.assertIsNotNone(self.decisioning.artifact_provider)
        self.assertEqual(self.decisioning.artifact_provider.subscription_count, 1)

    def test_initialize_updates_artifact_on_polling_interval(self):
        config = deepcopy(CONFIG)
        config.polling_interval = 1  # seconds
        self.decisioning = TargetDecisioningEngine(config)

        with patch("target_decisioning_engine.artifact_provider.get_min_polling_interval", return_value=0):
            with patch.object(PoolManager, "request", return_value=MOCK_ARTIFACT_RESPONSE) as artifact_request_mock:
                self.decisioning.initialize()

                time.sleep(5)

                self.assertGreaterEqual(artifact_request_mock.call_count, 4)
                artifact = self.decisioning.get_raw_artifact()
                self.assertIsNotNone(artifact)


    def test_initialize_error_fetching_artifact(self):
        config = deepcopy(CONFIG)
        config.polling_interval = 0
        config.event_emitter = Mock()
        self.decisioning = TargetDecisioningEngine(config)

        with patch.object(PoolManager, "request", return_value=MOCK_ARTIFACT_RESPONSE_BAD):
            with patch("target_decisioning_engine.artifact_provider.BACKOFF_FACTOR", 0):
                with self.assertRaises(Exception) as err:
                    self.decisioning.initialize()
                    self.assertEqual(json.loads(err.exception.body),
                                    {"status": 500, "message": "The decisioning artifact is not available"})
                    self.assertEqual(config.event_emitter.call_count, 11)  # validate retries
                    self.assertEqual(config.event_emitter.call_args[0][0], ARTIFACT_DOWNLOAD_FAILED)

    def test_get_offers(self):
        config = deepcopy(CONFIG)
        config.polling_interval = 0
        self.decisioning = TargetDecisioningEngine(config)

        with patch.object(PoolManager, "request", return_value=MOCK_ARTIFACT_RESPONSE):
            self.decisioning.initialize()

        get_offers_opts = TargetDeliveryRequest(request=TARGET_REQUEST, session_id="dummy_session")
        offers = self.decisioning.get_offers(get_offers_opts)
        self.assertIsNotNone(offers)

    def test_get_offers_unsupported_artifact_version(self):
        config = deepcopy(CONFIG)
        config.polling_interval = 0
        self.decisioning = TargetDecisioningEngine(config)

        with patch.object(PoolManager, "request", return_value=MOCK_ARTIFACT_RESPONSE_UNSUPPORTED_VERSION):
            self.decisioning.initialize()

        with self.assertRaises(Exception) as err:
            get_offers_opts = TargetDeliveryRequest(request=TARGET_REQUEST, session_id="dummy_session")
            self.decisioning.get_offers(get_offers_opts)
            self.assertEqual(json.loads(err.exception.body),
                             MESSAGES.get("ARTIFACT_VERSION_UNSUPPORTED")(ARTIFACT_UNSUPPORTED_VERSION.get("version"),
                                                                          SUPPORTED_ARTIFACT_MAJOR_VERSION))
