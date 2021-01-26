<<<<<<< HEAD
# Copyright 2020 Adobe. All rights reserved.
=======
# Copyright 2021 Adobe. All rights reserved.
>>>>>>> TNT-38924 getAttributes()
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

<<<<<<< HEAD
"""Assorted utility functions for target_tools package"""
# pylint: disable=protected-access

from delivery_api_client import ModelProperty as Property
from target_tools.enums import DecisioningMethod
from target_tools.logger import get_logger
from target_tools.messages import property_token_mismatch

logger = get_logger()


def requires_decisioning_engine(decisioning_method):
    """Determines if any decisioning is done on-device or not"""
    return decisioning_method in [DecisioningMethod.ON_DEVICE.value, DecisioningMethod.HYBRID.value]


def get_property_token(_property=None):
    """Get property token"""
    return _property.token if _property else None


def get_property(config, request):
    """Attempts to fetch property token from request and falls back to config"""
    if not config:
        config = {}

    config_property_token = config.get('property_token')
    request_property_token = get_property_token(request._property) if request else None
    property_token = request_property_token or config_property_token

    if request_property_token and request_property_token != config_property_token:
        logger.debug(
            property_token_mismatch(request_property_token, config_property_token)
        )

    return Property(token=property_token) if property_token else None


def decisioning_engine_ready(decisioning_engine):
    """Checks if decisioning engine is ready"""
    return decisioning_engine if decisioning_engine and decisioning_engine.is_ready() else None
=======
"""utils"""

MBOXES = "mboxes"


def get_names_for_requested(items_key, delivery_request):
    """
    :parameter
    items_key: str ('mboxes' | 'views')
    request: "import("../delivery-api-client/models/DeliveryRequest").DeliveryRequest" - Target View
        Delivery API request, required
    :returns
    mbox_names: set<str> - Set of mbox names
    """
    result_set = set()
    for request_type in ["prefetch", "execute"]:
        if delivery_request and delivery_request.get(request_type) and isinstance(
                delivery_request. get(request_type).get(items_key), list):
            items = delivery_request.get(request_type).get(items_key)
        else:
            items = []
        for item in items:
            result_set.add(item.get('name'))
    return result_set


def get_mbox_names(delivery_request):
    """
    :parameter
    request: "import("../delivery-api-client/models/DeliveryRequest").DeliveryRequest" - Target View
        Delivery API request, required
    :returns
    mbox_names: set<str> - Set of mbox names
    """
    return get_names_for_requested(MBOXES, delivery_request)


def add_mboxes_to_request(mbox_names, request, request_type="execute"):
    """The add_mboxes_to_request method
    Ensures the mboxes specified are part of the returned delivery request
    :parameter
    mbox_names: list<str> - A list of mbox names that contains JSON content attributes, required
    request: "import("../delivery-api-client/models/DeliveryRequest").DeliveryRequest" - Target View
        Delivery API request, required
    request_type: str ('execute'|'prefetch')
    """
<<<<<<< HEAD
    print(mbox_names, request, request_type)
    return request
>>>>>>> TNT-38924 getAttributes()
=======
    requested_mboxes = get_mbox_names(request)
    mboxes = []
    if request and request.get(request_type) and isinstance(
            request.get(request_type).get('mboxes'), list):
        mboxes.extend(request.get(request_type).get('mboxes'))

    highest_user_specified_index_mbox = max(
        mboxes, key=lambda mbox: mbox['index']).get('index') if mboxes else 0

    next_index = highest_user_specified_index_mbox + 1

    filtered_mbox_names = [
        mbox_name for mbox_name in mbox_names if mbox_name not in requested_mboxes]

    for mbox_name in filtered_mbox_names:
        mboxes.append({'name': mbox_name, 'index': next_index})
        next_index += 1

    result = request
    if request and request.get(request_type) and isinstance(
            request.get(request_type).get('mboxes'), list):
        result[request_type]['mboxes'] = mboxes

    return result
>>>>>>> Added utility methods
