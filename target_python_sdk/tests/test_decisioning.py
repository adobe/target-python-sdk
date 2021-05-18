# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for decisioning logic in TargetClient"""
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
import json
import time
import os
import unittest
from copy import deepcopy
from urllib3 import HTTPResponse

from delivery_api_client import DeliveryApi
from target_python_sdk import TargetClient
from target_tools.tests.helpers import expect_to_match_object
from target_tools.messages import DECISIONING_ENGINE_NOT_READY
from target_tools.tests.delivery_response_setup import create_delivery_response
from target_tools.utils import to_dict
from target_tools.enums import DecisioningMethod
from target_tools.tests.delivery_request_setup import create_delivery_request
from target_tools.tests.helpers import read_json_file
from target_decisioning_engine.constants import OK


ARTIFACT_AB_SIMPLE_FILE = "../../target_decisioning_engine/tests/schema/artifacts/TEST_ARTIFACT_AB_SIMPLE.json"
ARTIFACT_BLANK_FILE = "../../target_decisioning_engine/tests/schema/artifacts/TEST_ARTIFACT_BLANK.json"
CURRENT_DIR = os.path.dirname(__file__)
ARTIFACT_AB_SIMPLE = read_json_file(CURRENT_DIR, ARTIFACT_AB_SIMPLE_FILE)
ARTIFACT_BLANK = read_json_file(CURRENT_DIR, ARTIFACT_BLANK_FILE)

TARGET_REQUEST = create_delivery_request({
    "prefetch": {
        "mboxes": [{
            "name": "mbox-something",
            "index": 1
        }]
    }
})

REQUEST_BASE = {
    "id": {
        "tntId": "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
        "marketingCloudVisitorId": "07327024324407615852294135870030620007"
    },
    "context": {
        "channel": "web",
        "address": {
            "url": "http://adobe.com"
        },
        "userAgent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0"
    }
}

PREFETCH = {
    "prefetch": {
        "mboxes": [{
            "name": "mbox-magician",
            "index": 2
        }]
    }
}

EXECUTE = {
    "execute": {
        "mboxes": [{
            "name": "mbox-magician",
            "index": 2
        }]
    }
}

merged_prefetch = dict(REQUEST_BASE)
merged_prefetch.update(PREFETCH)
PREFETCH_REQUEST = create_delivery_request(merged_prefetch)

merged_execute = dict(REQUEST_BASE)
merged_execute.update(EXECUTE)
EXECUTE_REQUEST = create_delivery_request(merged_execute)

CONFIG = {
    "client": "someClientId",
    "organization_id": "someOrgId",
    "polling_interval": 0,
    "maximum_wait_ready": 500,
    "telemetry_enabled": False
}

LOCATION_HINT_RESPONSE = {
    "requestId": "1387f0ea-51d6-43df-ba32-f2fe79c356bd",
    "client": "someClientId",
    "id": {
        "tntId": "someSessionId.28_0"
    },
    "edgeHost": "mboxedge28.tt.omtrdc.net"
}


EXPECTED_PREFETCH_RESULT = {
    "request": {
        "requestId": "expect.any(String)",
        "id": {
            "tntId": "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
            "marketingCloudVisitorId": "07327024324407615852294135870030620007"
        },
        "context": {
            "channel": "web",
            "address": {
                "url": "http://adobe.com"
            },
            "userAgent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0"
        },
        "experienceCloud": {
            "analytics": {
                "logging": "server_side"
            }
        },
        "prefetch": {
            "mboxes": [
                {
                    "index": 2,
                    "name": "mbox-magician"
                }
            ]
        }
    },
    "target_cookie": {
        "name": "mbox",
        "value": "expect.any(String)",
        "maxAge": 63244800
    },
    "response": {
        "status": 200,
        "requestId": "expect.any(String)",
        "id": {
            "tntId": "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
            "marketingCloudVisitorId": "07327024324407615852294135870030620007"
        },
        "client": "someClientId",
        "prefetch": {
            "mboxes": [
                {
                    "index": 2,
                    "name": "mbox-magician",
                    "options": [
                        {
                            "content": {
                                "doMagic": True,
                                "importantValue": 150
                            },
                            "eventToken": "expect.any(String)",
                            "type": "json",
                            "responseTokens": "expect.any(Object)"
                        }
                    ]
                }
            ]
        }
    },
    "meta": {
        "decisioning_method": DecisioningMethod.ON_DEVICE.value,
        "remote_mboxes": [],
        "remote_views": []
    }
}

NOTIFICATION = {
    "notifications": [{
        "id": "expect.any(String)",
        "impressionId": "expect.any(String)",
        "timestamp": "expect.any(Number)",
        "type": "display",
        "mbox": {
          "name": "mbox-magician"
        },
        "tokens": ["expect.any(String)"]
    }]
}

EXPECTED_NOTIFICATION_REQUEST = dict(REQUEST_BASE)
EXPECTED_NOTIFICATION_REQUEST.update(NOTIFICATION)

DELIVERY_API_RESPONSE = {
  "status": 200,
  "requestId": "0979a315df524c74aa420a9d03c8d921",
  "client": "someClientId",
  "id": {
    "tntId": "338e3c1e51f7416a8e1ccba4f81acea0.28_0",
    "marketingCloudVisitorId": "07327024324407615852294135870030620007"
  },
  "edgeHost": "mboxedge28.tt.omtrdc.net",
  "prefetch": {
    "mboxes": [
      {
        "index": 2,
        "name": "mbox-magician",
        "options": [
          {
            "content": {"doMagic": True, "importantValue": 150},
            "type": "json",
            "eventToken":
              "abzfLHwlBDBNtz9ALey2fJNWHtnQtQrJfmRrQugEa2qCnQ9Y9OaLL2gsdrWQTvE54PwSz67rmXWmSnkXpSSS2Q==",
            "responseTokens": {}
          }
        ]
      }
    ]
  }
}


class TestTargetClientDecisioning(unittest.TestCase):

    def test_create_decisioning_method_on_device(self):
        client_ready_mock = Mock()
        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.ON_DEVICE.value
        client_opts["events"] = {
            "clientReady": client_ready_mock
        }

        with patch("target_decisioning_engine.artifact_provider.urllib3.PoolManager") as mock_pool_manager:
            instance = mock_pool_manager.return_value
            mock_response = HTTPResponse(status=OK, body=json.dumps(ARTIFACT_BLANK))
            instance.request.return_value = mock_response

            with patch.object(DeliveryApi, "execute", return_value=create_delivery_response(LOCATION_HINT_RESPONSE)):
                client = TargetClient.create(client_opts)
                self.assertIsNotNone(client.decisioning_engine)
                self.assertTrue(callable(client.decisioning_engine.get_offers))
                self.assertEqual(client_ready_mock.call_count, 1)

    def test_create_decisioning_method_server_side(self):
        client_ready_mock = Mock()
        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.SERVER_SIDE.value
        client_opts["events"] = {
            "clientReady": client_ready_mock
        }

        client = TargetClient.create(client_opts)
        time.sleep(1)
        self.assertIsNotNone(client)
        self.assertIsNone(client.decisioning_engine)
        self.assertEqual(client_ready_mock.call_count, 1)

    def test_get_offers_artifact_retrieval_failed(self):
        client_ready_mock = Mock()
        artifact_failed_mock = Mock()
        artifact_success_mock = Mock()

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.ON_DEVICE.value
        client_opts["events"] = {
            "clientReady": client_ready_mock,
            "artifactDownloadFailed": artifact_failed_mock,
            "artifactDownloadSucceeded": artifact_success_mock
        }

        with patch("target_decisioning_engine.artifact_provider.urllib3.PoolManager") as mock_pool_manager:
            instance = mock_pool_manager.return_value
            mock_response = HTTPResponse(status=403)
            instance.request.return_value = mock_response

            with patch.object(DeliveryApi, "execute", return_value=create_delivery_response(LOCATION_HINT_RESPONSE)):
                client = TargetClient.create(client_opts)

                self.assertEqual(client_ready_mock.call_count, 0)
                self.assertEqual(artifact_success_mock.call_count, 0)
                self.assertEqual(artifact_failed_mock.call_count, 1)
                self.assertEqual(artifact_failed_mock.call_args[0][0].get("type"), "artifactDownloadFailed")
                self.assertIsNotNone(artifact_failed_mock.call_args[0][0].get("artifact_location"))
                self.assertIsNotNone(artifact_failed_mock.call_args[0][0].get("error"))

                get_offers_opts = {
                    "request": TARGET_REQUEST,
                    "session_id": "dummy_session"
                }

            with self.assertRaises(Exception) as err:
                client.get_offers(get_offers_opts)
                self.assertEqual(str(err.exception), DECISIONING_ENGINE_NOT_READY)

    def test_client_preemptively_fetches_target_location_hint(self):
        get_offers_opts = {
            "request": TARGET_REQUEST,
            "session_id": "dummy_session"
        }

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.ON_DEVICE.value

        with patch("target_decisioning_engine.artifact_provider.urllib3.PoolManager") as mock_artifact_provider:
            artifact_instance = mock_artifact_provider.return_value
            artifact_response = HTTPResponse(status=OK, body=json.dumps(ARTIFACT_AB_SIMPLE))
            artifact_instance.request.return_value = artifact_response

            with patch.object(DeliveryApi, "execute", return_value=create_delivery_response(LOCATION_HINT_RESPONSE)):
                client = TargetClient.create(client_opts)
                result = client.get_offers(get_offers_opts)  # on-device
                self.assertEqual(result.get("target_location_hint_cookie"), {
                    "name": "mboxEdgeCluster",
                    "value": "28",
                    "maxAge": 1860
                })

    def test_client_recovers_if_location_hint_request_fails(self):
        get_offers_opts = {
            "request": TARGET_REQUEST,
            "session_id": "dummy_session"
        }

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.ON_DEVICE.value

        with patch("delivery_api_client.rest.urllib3.PoolManager") as mock_delivery_api:
            delivery_instance = mock_delivery_api.return_value
            delivery_response = HTTPResponse(status=503)
            delivery_instance.request.return_value = delivery_response

            with patch("target_decisioning_engine.artifact_provider.urllib3.PoolManager") as mock_artifact_provider:
                artifact_instance = mock_artifact_provider.return_value
                artifact_response = HTTPResponse(status=OK, body=json.dumps(ARTIFACT_AB_SIMPLE))
                artifact_instance.request.return_value = artifact_response

                client = TargetClient.create(client_opts)
                result = client.get_offers(get_offers_opts)  # on-device
                self.assertIsNone(result.get("target_location_hint_cookie"))

    def test_client_uses_location_hint_from_config(self):
        get_offers_opts = {
            "request": TARGET_REQUEST,
            "session_id": "dummy_session"
        }

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.ON_DEVICE.value
        client_opts["target_location_hint"] = "28"

        with patch("target_decisioning_engine.artifact_provider.urllib3.PoolManager") as mock_artifact_provider:
            artifact_instance = mock_artifact_provider.return_value
            artifact_response = HTTPResponse(status=OK, body=json.dumps(ARTIFACT_AB_SIMPLE))
            artifact_instance.request.return_value = artifact_response

            client = TargetClient.create(client_opts)
            result = client.get_offers(get_offers_opts)
            self.assertEqual(result.get("target_location_hint_cookie"), {
                "name": "mboxEdgeCluster",
                "value": "28",
                "maxAge": 1860
            })

    def test_get_offers_valid_on_device_decisioning_response(self):
        get_offers_opts = {
            "request": PREFETCH_REQUEST,
            "session_id": "dummy_session"
        }

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.ON_DEVICE.value
        client_opts["target_location_hint"] = "28"

        with patch("target_decisioning_engine.artifact_provider.urllib3.PoolManager") as mock_artifact_provider:
            artifact_instance = mock_artifact_provider.return_value
            artifact_response = HTTPResponse(status=OK, body=json.dumps(ARTIFACT_AB_SIMPLE))
            artifact_instance.request.return_value = artifact_response

            with patch.object(DeliveryApi, "execute", return_value=create_delivery_response(LOCATION_HINT_RESPONSE)):
                client = TargetClient.create(client_opts)
                result = client.get_offers(get_offers_opts)
                result_dict = to_dict(result)
                expect_to_match_object(result_dict, EXPECTED_PREFETCH_RESULT)

    def test_get_offers_on_device_decisioning_emits_notifications(self):
        get_offers_opts = {
            "request": EXECUTE_REQUEST,
            "session_id": "dummy_session"
        }

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.ON_DEVICE.value
        client_opts["target_location_hint"] = "28"

        # send_notifications call
        with patch.object(DeliveryApi, "execute", return_value=create_delivery_response({})) \
                as mock_delivery_api:

            with patch("target_decisioning_engine.artifact_provider.urllib3.PoolManager") as mock_artifact_provider:
                artifact_instance = mock_artifact_provider.return_value
                artifact_response = HTTPResponse(status=OK, body=json.dumps(ARTIFACT_AB_SIMPLE))
                artifact_instance.request.return_value = artifact_response

                client = TargetClient.create(client_opts)
                self.assertEqual(mock_artifact_provider.call_count, 1)

                result = client.get_offers(get_offers_opts)
                self.assertIsNotNone(result.get("response"))
                self.assertEqual(result.get("response").status, OK)
                self.assertIsNotNone(result.get("response").execute)

                time.sleep(1)  # notifications sent async
                self.assertEqual(mock_delivery_api.call_count, 1)
                notification_request = to_dict(mock_delivery_api.call_args[0][2])
                expect_to_match_object(notification_request, EXPECTED_NOTIFICATION_REQUEST)

    def test_get_offers_server_side(self):
        expected_result = deepcopy(EXPECTED_PREFETCH_RESULT)
        expected_result["response"]["edgeHost"] = "mboxedge28.tt.omtrdc.net"
        expected_result["target_location_hint_cookie"] = {
            "name": "mboxEdgeCluster",
            "value": "28",
            "maxAge": 1860
        }
        expected_result["meta"] = {
            "decisioning_method": DecisioningMethod.SERVER_SIDE.value
        }

        get_offers_opts = {
            "request": PREFETCH_REQUEST,
            "session_id": "dummy_session"
        }

        client_opts = dict(CONFIG)
        client_opts["decisioning_method"] = DecisioningMethod.SERVER_SIDE.value

        with patch.object(DeliveryApi, "execute", return_value=create_delivery_response(DELIVERY_API_RESPONSE)):
            client = TargetClient.create(client_opts)
            result = client.get_offers(get_offers_opts)
            result_dict = to_dict(result)
            expect_to_match_object(result_dict, expected_result)
