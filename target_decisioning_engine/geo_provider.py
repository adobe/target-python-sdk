# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""GeoProvider class and related functions"""
try:
    from functools import reduce
except ImportError:
    pass
try:
    from queue import Queue
except ImportError:
    from Queue import Queue
import json
from threading import Thread
from copy import deepcopy
import urllib3
from delivery_api_client import Geo
from target_tools.logger import get_logger
from target_tools.utils import noop
from target_tools.utils import parse_float
from target_decisioning_engine.constants import HTTP_GET
from target_decisioning_engine.constants import OK
from target_decisioning_engine.events import GEO_LOCATION_UPDATED
from target_decisioning_engine.utils import get_geo_lookup_path
from target_decisioning_engine.constants import HTTP_HEADER_FORWARDED_FOR
from target_decisioning_engine.constants import HTTP_HEADER_GEO_LATITUDE
from target_decisioning_engine.constants import HTTP_HEADER_GEO_LONGITUDE
from target_decisioning_engine.constants import HTTP_HEADER_GEO_COUNTRY
from target_decisioning_engine.constants import HTTP_HEADER_GEO_REGION
from target_decisioning_engine.constants import HTTP_HEADER_GEO_CITY


GEO_MAPPINGS = [
    {
        "header_name": HTTP_HEADER_FORWARDED_FOR,
        "parse_value": False,
        "value_key": "ip_address"
    },
    {
        "header_name": HTTP_HEADER_GEO_LATITUDE,
        "parse_value": parse_float,
        "value_key": "latitude"
    },
    {
        "header_name": HTTP_HEADER_GEO_LONGITUDE,
        "parse_value": parse_float,
        "value_key": "longitude"
    },
    {
        "header_name": HTTP_HEADER_GEO_COUNTRY,
        "parse_value": False,
        "value_key": "country_code"
    },
    {
        "header_name": HTTP_HEADER_GEO_REGION,
        "parse_value": False,
        "value_key": "state_code"
    },
    {
        "header_name": HTTP_HEADER_GEO_CITY,
        "parse_value": False,
        "value_key": "city"
    }
]


def _map_geo_values(value_fn, initial=None):
    """
    :param value_fn: (callable) function to lookup value by key
    :param initial: (delivery_api_client.Model.geo.Geo) initial geo object to start reduce with
    :return: (delivery_api_client.Model.geo.Geo) geo object
    """
    if not initial:
        initial = Geo()

    def geo_mapping_accumulator(result, geo_mapping):
        """
        :param result: (delivery_api_client.Model.geo.Geo) geo object
        :param geo_mapping: (dict) mapping object for handling specific geo fields
        :return: (delivery_api_client.Model.geo.Geo) updated result
        """
        value = value_fn(geo_mapping.get("header_name"))
        if value:
            value = geo_mapping.get("parse_value")(value) if geo_mapping.get("parse_value") else value
            setattr(result, geo_mapping.get("value_key"), value)
        return result

    return reduce(geo_mapping_accumulator, GEO_MAPPINGS, initial)


def create_or_update_geo_object(geo_data=None, existing_geo_context=None):
    """
    :param existing_geo_context: (delivery_api_client.Model.geo.Geo) geo object
    :param geo_data: (dict) geo payload or headers to merge into existing_geo_context
    :return: (delivery_api_client.Model.geo.Geo) geo object
    """
    if not geo_data:
        geo_data = {}

    def _get_payload(key):
        return geo_data.get(key)

    return _map_geo_values(_get_payload, existing_geo_context)


def is_missing_geo_fields(geo_request_context):
    """
    :param geo_request_context: (delivery_api_client.Model.geo.Geo) geo object
    :return: (bool) Returns True if specified geo fields are undefined, else False
    """
    return not geo_request_context.latitude and not geo_request_context.longitude and not \
        geo_request_context.country_code and not geo_request_context.state_code and not geo_request_context.city


class GeoProvider:
    """GeoProvider"""

    def __init__(self, config, artifact):
        """
        :param config: (target_decisioning_engine.types.decisioning_config.DecisioningConfig) config
        :param artifact: (target_decisioning_engine.types.decisioning_artifact.DecisioningArtifact) artifact
        """
        self.logger = get_logger()
        self.pool_manager = urllib3.PoolManager()
        self.config = config
        self.artifact = artifact
        self.geo_targeting_enabled = artifact.get("geoTargetingEnabled", False)
        self.event_emitter = config.event_emitter or noop

    def _execute_request(self, geo_lookup_path, headers, queue):
        """Sends http request for geo data"""
        response = self.pool_manager.request(HTTP_GET, geo_lookup_path, headers=headers)
        queue.put(response)

    def _request_geo(self, geo_lookup_path, headers):
        """Executes geo request in a new thread"""
        result = Queue()
        request_thread = Thread(target=self._execute_request,
                                name="GeoProvider.request",
                                args=[geo_lookup_path, headers, result])
        request_thread.start()
        request_thread.join()
        return result.get()

    def valid_geo_request_context(self, geo_request_context=None):
        """
        :param geo_request_context: (delivery_api_client.Model.geo.Geo) geo object
        :return: (delivery_api_client.Model.geo.Geo) geo object
        """
        if not geo_request_context:
            geo_request_context = Geo()

        validated_geo_request_context = deepcopy(geo_request_context)

        # When ipAddress is the only geo value passed in to getOffers(), do IP-to-Geo lookup.
        geo_lookup_path = get_geo_lookup_path(self.config)

        if self.geo_targeting_enabled and is_missing_geo_fields(geo_request_context):
            headers = {}

            if geo_request_context.ip_address:
                headers[HTTP_HEADER_FORWARDED_FOR] = geo_request_context.ip_address

            try:
                response = self._request_geo(geo_lookup_path, headers)
                return self.geo_response_handler(response, validated_geo_request_context)
            except Exception as err:
                self.logger.error("Exception while fetching geo data at: {} - error: {}".format(geo_lookup_path,
                                                                                                (str(err))))
                return None

        return validated_geo_request_context

    def geo_response_handler(self, response, validated_geo_request_context):
        """Process geo response"""
        if response.status != OK:
            self.logger.error("{} status code while fetching geo data at: {} - message: {}".format(
                response.status,
                response,
                response.data)
            )
            return None

        geo_payload = json.loads(response.data)
        validated_geo_request_context = create_or_update_geo_object(
            geo_data=geo_payload,
            existing_geo_context=validated_geo_request_context
        )

        self.event_emitter(GEO_LOCATION_UPDATED, {
            "geo_context": validated_geo_request_context
        })

        return validated_geo_request_context
