# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for taraget_decisioning_engine.geo_provider module"""
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import json
import os
import unittest
from copy import deepcopy
from urllib3 import HTTPResponse
from delivery_api_client import Geo
from target_decisioning_engine.geo_provider import create_or_update_geo_object
from target_decisioning_engine.geo_provider import GeoProvider
from target_decisioning_engine.types.decisioning_config import DecisioningConfig
from target_decisioning_engine.constants import HTTP_HEADER_FORWARDED_FOR, BAD_REQUEST
from target_decisioning_engine.constants import OK
from target_python_sdk.tests.helpers import read_json_file

CURRENT_DIR = os.path.dirname(__file__)
ARTIFACT_BLANK = read_json_file(CURRENT_DIR, "schema/artifacts/TEST_ARTIFACT_BLANK.json")


class TestGeoProvider(unittest.TestCase):
    """TestGeoProvider"""

    def setUp(self):
        self.headers = {
            "x-geo-latitude": 37.773972,
            "x-geo-longitude": -122.431297,
            "x-geo-country-code": "US",
            "x-geo-region-code": "CA",
            "x-geo-city": "SANFRANCISCO"
        }
        self.config = DecisioningConfig("myClient", "myOrgId")
        geo_values = {
            "x-geo-longitude": -122.4,
            "x-geo-latitude": 37.75,
            "x-geo-city": "SAN FRANCISCO",
            "x-geo-region-code": "CA",
            "x-geo-country-code": "US"
        }
        self.mock_geo_response = HTTPResponse(body=json.dumps(geo_values), status=OK)

    def test_create_or_update_geo_object_no_existing_and_empty_geo_data(self):
        result = create_or_update_geo_object()
        expected = Geo()
        self.assertEqual(result, expected)

    def test_create_or_update_geo_object_no_existing(self):
        result = create_or_update_geo_object(geo_data=self.headers)
        expected = Geo(**{
            "latitude": 37.773972,
            "longitude": -122.431297,
            "city": "SANFRANCISCO",
            "country_code": "US",
            "state_code": "CA"
        })
        self.assertEqual(result, expected)

    def test_create_or_update_geo_object_merge_with_existing(self):
        existing_geo = Geo(latitude=37.773972, longitude=-122.431297)
        headers = {
            "x-geo-country-code": "US",
            "x-geo-region-code": "CA",
            "x-geo-city": "SANFRANCISCO"
        }
        result = create_or_update_geo_object(geo_data=headers, existing_geo_context=existing_geo)
        expected = Geo(**{
            "latitude": 37.773972,
            "longitude": -122.431297,
            "city": "SANFRANCISCO",
            "country_code": "US",
            "state_code": "CA"
        })
        self.assertEqual(result, expected)

    def test_create_or_update_geo_object_empty_geo_data(self):
        existing_geo = Geo(latitude=37.773972, longitude=-122.431297)
        result = create_or_update_geo_object(geo_data=None, existing_geo_context=existing_geo)
        expected = Geo(**{
            "latitude": 37.773972,
            "longitude": -122.431297
        })
        self.assertEqual(result, expected)

    def test_valid_geo_request_context_geo_targeting_disabled(self):
        artifact = deepcopy(ARTIFACT_BLANK)
        artifact["geoTargetingEnabled"] = False
        geo_provider = GeoProvider(self.config, artifact)

        with patch.object(geo_provider.pool_manager, "request", return_value=self.mock_geo_response) as mock_http_call:
            geo_input = Geo(ip_address="12.21.1.40")
            result = geo_provider.valid_geo_request_context(geo_input)

            self.assertEqual(result, geo_input)
            self.assertEqual(mock_http_call.call_count, 0)

    def test_valid_geo_request_context_geo_targeting_enabled_and_valid_ip_address(self):
        expected = Geo(**{
            "city": "SAN FRANCISCO",
            "country_code": "US",
            "ip_address": "12.21.1.40",
            "latitude": 37.75,
            "longitude": -122.4,
            "state_code": "CA"
        })
        artifact = deepcopy(ARTIFACT_BLANK)
        artifact["geoTargetingEnabled"] = True
        geo_provider = GeoProvider(self.config, artifact)

        with patch.object(geo_provider.pool_manager, "request", return_value=self.mock_geo_response) as mock_http_call:
            geo_input = Geo(ip_address="12.21.1.40")
            result = geo_provider.valid_geo_request_context(geo_input)

            self.assertEqual(result, expected)
            self.assertEqual(mock_http_call.call_count, 1)
            self.assertEqual(mock_http_call.call_args[0][1], "https://assets.adobetarget.com/v1/geo")
            self.assertEqual(mock_http_call.call_args[1].get("headers").get(HTTP_HEADER_FORWARDED_FOR), "12.21.1.40")

    def test_valid_geo_request_context_no_ip_address(self):
        expected = Geo(**{
            "city": "SAN FRANCISCO",
            "country_code": "US",
            "latitude": 37.75,
            "longitude": -122.4,
            "state_code": "CA"
        })
        artifact = deepcopy(ARTIFACT_BLANK)
        artifact["geoTargetingEnabled"] = True
        geo_provider = GeoProvider(self.config, artifact)

        with patch.object(geo_provider.pool_manager, "request", return_value=self.mock_geo_response) as mock_http_call:
            geo_input = Geo(ip_address=None)
            result = geo_provider.valid_geo_request_context(geo_input)

            self.assertEqual(result, expected)
            self.assertEqual(mock_http_call.call_count, 1)
            self.assertEqual(mock_http_call.call_args[0][1], "https://assets.adobetarget.com/v1/geo")
            self.assertIsNone(mock_http_call.call_args[1].get("headers").get(HTTP_HEADER_FORWARDED_FOR))

    def test_valid_geo_request_context_not_missing_geo_fields(self):
        expected = Geo(city="Las Vegas")
        artifact = deepcopy(ARTIFACT_BLANK)
        artifact["geoTargetingEnabled"] = True
        geo_provider = GeoProvider(self.config, artifact)

        with patch.object(geo_provider.pool_manager, "request", return_value=self.mock_geo_response) as mock_http_call:
            geo_input = Geo(ip_address=None, city="Las Vegas")
            result = geo_provider.valid_geo_request_context(geo_input)

            self.assertEqual(result, expected)
            self.assertEqual(mock_http_call.call_count, 0)

    def test_valid_geo_request_non_200_response(self):
        artifact = deepcopy(ARTIFACT_BLANK)
        artifact["geoTargetingEnabled"] = True
        geo_provider = GeoProvider(self.config, artifact)

        mock_bad_response = HTTPResponse(body="Bad Request", status=BAD_REQUEST)
        with patch.object(geo_provider.pool_manager, "request", return_value=mock_bad_response) as mock_http_call:
            geo_input = Geo(ip_address="12.21.1.40")
            result = geo_provider.valid_geo_request_context(geo_input)

            self.assertEqual(result, None)
            self.assertEqual(mock_http_call.call_count, 1)
            self.assertEqual(mock_http_call.call_args[0][1], "https://assets.adobetarget.com/v1/geo")
            self.assertEqual(mock_http_call.call_args[1].get("headers").get(HTTP_HEADER_FORWARDED_FOR), "12.21.1.40")

    def test_geo_invalid_ip_address(self):
        with self.assertRaises(ValueError) as err:
            Geo(ip_address="277.0.0.1")
            self.assertEqual(str(err.exception), r"""Invalid value for `ip_address`, must be a follow pattern or equal
            to `/((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]
            |25[0-5]))\s*$)|(^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}
            |((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:
            [0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([
            0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(
            25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]
            {1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]
            {1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25
            [0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]
            {1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-
            f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]
            ?\d)){3}))|:)))(%.+)?\s*$))/`""")
