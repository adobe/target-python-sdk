# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Assorted utility functions for target_tools package"""
# pylint: disable=protected-access

from delivery_api_client import ModelProperty as Property
from target_tools.enums import DecisioningMethod
from target_tools.logger import get_logger
from target_tools.messages import property_token_mismatch
from target_tools.constants import REQUEST_TYPES
from target_python_sdk.utils import is_list


MBOXES = "mboxes"

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


def get_names_for_requested(items_key, delivery_request):
    """
    :param items_key: ('mboxes' | 'views')
    request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target View Delivery API request, required
    :returns
    mbox_names: (set) Set of mbox names
    """
    result_set = set()
    for request_type in REQUEST_TYPES:
        request_item = getattr(delivery_request, request_type, {})
        for item in getattr(request_item, items_key, []) or []:
            result_set.add(item.name)
    return result_set


def get_mbox_names(delivery_request):
    """
    :param request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target View Delivery API request, required
    :returns
    mbox_names: (set) Set of mbox names
    """
    return get_names_for_requested(MBOXES, delivery_request)


def add_mboxes_to_request(mbox_names, request, request_type="execute"):
    """The add_mboxes_to_request method
    Ensures the mboxes specified are part of the returned delivery request
    :param mbox_names: (list) A list of mbox names that contains JSON content attributes, required
    request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target View Delivery API request, required
    request_type: ('execute'|'prefetch')
    """
    requested_mboxes = get_mbox_names(request)
    mboxes = []
    if not request or not getattr(request, request_type, {}) or not is_list(
            getattr(request, request_type, {}).mboxes):
        return request

    mboxes.extend(getattr(request, request_type, {}).mboxes)

    highest_user_specified_index_mbox = max(
        mboxes, key=lambda mbox: mbox.index).index if mboxes else 0

    next_index = highest_user_specified_index_mbox + 1

    for mbox_name in (name for name in mbox_names if name not in requested_mboxes):
        mboxes.append({'name': mbox_name, 'index': next_index})
        next_index += 1

    result = request

    getattr(result, request_type).mboxes = mboxes

    return result
