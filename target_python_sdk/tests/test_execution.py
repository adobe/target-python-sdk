# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for execution logic in TargetClient"""
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import json
import os
import unittest
from urllib3 import HTTPResponse
from delivery_api_client import DeliveryApi
from target_decisioning_engine.constants import OK
from target_decisioning_engine.constants import PARTIAL_CONTENT
from target_python_sdk import TargetClient
from target_tools.enums import DecisioningMethod
from target_tools.messages import DECISIONING_ENGINE_NOT_READY
from target_tools.tests.delivery_request_setup import create_delivery_request
from target_tools.tests.delivery_response_setup import create_delivery_response
from target_tools.tests.helpers import read_json_file


ARTIFACT_FEATURE_FLAG_FILE = "../../target_decisioning_engine/tests/schema/artifacts/TEST_ARTIFACT_FEATURE_FLAG.json"
CURRENT_DIR = os.path.dirname(__file__)
FEATURE_FLAG_ARTIFACT = read_json_file(CURRENT_DIR, ARTIFACT_FEATURE_FLAG_FILE)

CONFIG = {
    "client": "someClientId",
    "organization_id": "someOrgId",
    "target_location_hint": "28",
    "polling_interval": 0,
    "maximum_wait_ready": 500,
    "telemetry_enabled": False
}

context = {
    "channel": "web",
    "address": {
        "url": "http://adobe.com"
    },
    "userAgent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0"
}

visitor_id = {
    "tntId": "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
    "marketingCloudVisitorId": "07327024324407615852294135870030620007"
}

TARGET_REQUEST_DICT = {
    "id": visitor_id,
    "context": context
}

DELIVERY_RESPONSE = {
    "status": 200,
    "requestId": "7a568cbfe3f44f0b99d1092c246660c3",
    "client": "targettesting",
    "id": {
        "tntId": "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
        "marketingCloudVisitorId": "07327024324407615852294135870030620007"
    },
    "edgeHost": "mboxedge28.tt.omtrdc.net",
    "prefetch": {
        "mboxes": [
            {
                "index": 1,
                "name": "mbox-feature-flags",
                "options": [
                    {
                        "content": {
                            "paymentExperience": "alpha10",
                            "showFeatureX": True,
                            "paymentGatewayVersion": 3.1,
                            "customerFeedbackValue": 99
                        },
                        "type": "json",
                        "eventToken":
                            "8MDICvd7bsTPYn79fLBNQpNWHtnQtQrJfmRrQugEa2qCnQ9Y9OaLL2gsdrWQTvE54PwSz67rmXWmSnkXpSSS2Q=="
                    }
                ]
            },
            {
                "index": 2,
                "name": "remote-only-mbox-a",
                "options": [
                    {
                        "content": {
                            "paymentExperience": "alpha10",
                            "showFeatureX": True,
                            "paymentGatewayVersion": 3.1,
                            "customerFeedbackValue": 99
                        },
                        "type": "json",
                        "eventToken":
                            "8MDIALF7bsTPYn79fLBNQpNWHtnQtQrJfmRrQugEa2qCnQ9Y9OaLL2gsdrWQTvE54PwSz67rmXWmSnkXpSSS2Q=="
                    }
                ]
            }
        ]
    }
}


class TestTargetClientExecution(unittest.TestCase):

    def test_get_offers_on_device_partial_returns_206_and_remote_mbox_names(self):
        get_offers_opts = {
            "request": TARGET_REQUEST_DICT,
            "session_id": "dummy_session"
        }
        get_offers_opts["request"]["prefetch"] = {
            "mboxes": [
                {
                    "name": "mbox-feature-flags",
                    "index": 1
                },
                {
                    "name": "remote-only-mbox-a",
                    "index": 2
                },
                {
                    "name": "remote-only-mbox-b",
                    "index": 2
                }
            ]
        }
        get_offers_opts["request"] = create_delivery_request(get_offers_opts["request"])

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.ON_DEVICE.value

        with patch("target_decisioning_engine.artifact_provider.urllib3.PoolManager") as mock_artifact_provider:
            artifact_instance = mock_artifact_provider.return_value
            artifact_response = HTTPResponse(status=OK, body=json.dumps(FEATURE_FLAG_ARTIFACT))
            artifact_instance.request.return_value = artifact_response

            client = TargetClient.create(client_opts)
            self.assertEqual(mock_artifact_provider.call_count, 1)

            result = client.get_offers(get_offers_opts)
            self.assertEqual(result["response"].status, PARTIAL_CONTENT)
            self.assertIsNotNone(result["response"].prefetch)
            self.assertEqual(result["meta"]["decisioning_method"], DecisioningMethod.ON_DEVICE.value)
            self.assertSetEqual(set(result["meta"]["remote_mboxes"]), set(["remote-only-mbox-a", "remote-only-mbox-b"]))
            self.assertEqual(result["meta"]["remote_views"], [])

    def test_get_offers_on_device_returns_200_if_no_mboxes_require_remote(self):
        get_offers_opts = {
            "request": TARGET_REQUEST_DICT,
            "session_id": "dummy_session"
        }
        get_offers_opts["request"]["prefetch"] = {
            "mboxes": [
                {
                    "name": "mbox-feature-flags",
                    "index": 1
                }
            ]
        }
        get_offers_opts["request"] = create_delivery_request(get_offers_opts["request"])

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.ON_DEVICE.value

        with patch("target_decisioning_engine.artifact_provider.urllib3.PoolManager") as mock_artifact_provider:
            artifact_instance = mock_artifact_provider.return_value
            artifact_response = HTTPResponse(status=OK, body=json.dumps(FEATURE_FLAG_ARTIFACT))
            artifact_instance.request.return_value = artifact_response

            client = TargetClient.create(client_opts)
            self.assertEqual(mock_artifact_provider.call_count, 1)

            result = client.get_offers(get_offers_opts)
            self.assertEqual(result["response"].status, OK)
            self.assertIsNotNone(result["response"].prefetch)
            self.assertEqual(result["meta"]["decisioning_method"], DecisioningMethod.ON_DEVICE.value)
            self.assertEqual(result["meta"]["remote_mboxes"], [])
            self.assertEqual(result["meta"]["remote_views"], [])

    def test_get_offers_hybrid_does_remote_request_if_necessary(self):
        get_offers_opts = {
            "request": TARGET_REQUEST_DICT,
            "session_id": "dummy_session"
        }
        get_offers_opts["request"]["prefetch"] = {
            "mboxes": [
                {
                    "name": "mbox-feature-flags",
                    "index": 1
                },
                {
                    "name": "remote-only-mbox-a",
                    "index": 2
                },
                {
                    "name": "remote-only-mbox-b",
                    "index": 2
                }
            ]
        }
        get_offers_opts["request"] = create_delivery_request(get_offers_opts["request"])

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.HYBRID.value

        with patch.object(DeliveryApi, "execute", return_value=create_delivery_response(DELIVERY_RESPONSE)) \
                as mock_delivery_api:
            with patch("target_decisioning_engine.artifact_provider.urllib3.PoolManager") as mock_artifact_provider:
                artifact_instance = mock_artifact_provider.return_value
                artifact_response = HTTPResponse(status=OK, body=json.dumps(FEATURE_FLAG_ARTIFACT))
                artifact_instance.request.return_value = artifact_response

                client = TargetClient.create(client_opts)
                self.assertEqual(mock_artifact_provider.call_count, 1)

                result = client.get_offers(get_offers_opts)
                self.assertEqual(mock_delivery_api.call_count, 1)
                self.assertEqual(result["response"].status, OK)
                self.assertIsNotNone(result["response"].prefetch)
                self.assertEqual(result["meta"]["decisioning_method"], DecisioningMethod.HYBRID.value)
                self.assertSetEqual(set(result["meta"]["remote_mboxes"]),
                                    set(["remote-only-mbox-a", "remote-only-mbox-b"]))
                self.assertEqual(result["meta"]["remote_views"], [])

    def test_get_offers_raises_exception_if_client_configured_as_server_side_but_request_made_with_on_device(self):
        get_offers_opts = {
            "request": TARGET_REQUEST_DICT,
            "session_id": "dummy_session",
            "decisioning_method": DecisioningMethod.ON_DEVICE.value
        }
        get_offers_opts["request"]["prefetch"] = {
            "mboxes": [
                {
                    "name": "mbox-feature-flags",
                    "index": 1
                }
            ]
        }
        get_offers_opts["request"] = create_delivery_request(get_offers_opts["request"])

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.SERVER_SIDE.value
        client = TargetClient.create(client_opts)

        with self.assertRaises(Exception) as err:
            client.get_offers(get_offers_opts)
            self.assertEqual(str(err.exception), DECISIONING_ENGINE_NOT_READY)

    def test_get_offers_does_remote_request_if_hybrid_request_and_decisioning_engine_not_ready(self):
        get_offers_opts = {
            "request": TARGET_REQUEST_DICT,
            "session_id": "dummy_session",
            "decisioning_method": DecisioningMethod.HYBRID.value
        }
        get_offers_opts["request"]["prefetch"] = {
            "mboxes": [
                {
                    "name": "mbox-feature-flags",
                    "index": 1
                }
            ]
        }
        get_offers_opts["request"] = create_delivery_request(get_offers_opts["request"])

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.SERVER_SIDE.value

        with patch.object(DeliveryApi, "execute", return_value=create_delivery_response(DELIVERY_RESPONSE)) \
                as mock_delivery_api:
            client = TargetClient.create(client_opts)
            result = client.get_offers(get_offers_opts)
            self.assertEqual(mock_delivery_api.call_count, 1)
            self.assertEqual(result["response"].status, OK)
            self.assertIsNotNone(result["response"].prefetch)
            self.assertEqual(result["meta"]["decisioning_method"], DecisioningMethod.SERVER_SIDE.value)
            self.assertEqual(result["meta"]["remote_mboxes"], [])
            self.assertEqual(result["meta"]["remote_views"], [])
