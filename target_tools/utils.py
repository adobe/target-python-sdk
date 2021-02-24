# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Assorted utility functions for target_tools package"""
# pylint: disable=protected-access

from delivery_api_client import ModelProperty as Property
from target_tools.constants import REQUEST_TYPES
from target_tools.enums import DecisioningMethod
from target_tools.logger import get_logger
from target_tools.messages import property_token_mismatch

VIEWS = "views"
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


def has_requested(items_key, delivery_request):
    """
    :param items_key: ("mboxes"|"views") key, required
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target Delivery API request, required
    :return: (bool) Does request include items_key
    """
    for _type in REQUEST_TYPES:
        if delivery_request and getattr(delivery_request, _type, None) \
                and getattr(getattr(delivery_request, _type, {}), items_key, None):
            return True
    return False


def has_requested_views(delivery_request):
    """
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target Delivery API request, required
    :return: (bool) Does request include views
    """
    return has_requested(VIEWS, delivery_request)


def get_names_for_requested(items_key, delivery_request):
    """
    :param items_key: ("mboxes"|"views") key, required
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target Delivery API request, required
    :return: (set<str>) Set of names
    """
    result_set = set()

    for _type in REQUEST_TYPES:
        if delivery_request and getattr(delivery_request, _type, None) \
                and getattr(getattr(delivery_request, _type, {}), items_key, None):
            items = getattr(getattr(delivery_request, _type, {}), items_key, [])
            for item in (item for item in items if item.name):
                result_set.add(item.name)

    return result_set


def get_mbox_names(delivery_request):
    """
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target Delivery API request, required
    :return: (set<str>) Set of mbox names
    """
    return get_names_for_requested(MBOXES, delivery_request)


def get_view_names(delivery_request):
    """
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target Delivery API request, required
    :return: (set<str>) Set of view names
    """
    return get_names_for_requested(VIEWS, delivery_request)


def noop():
    """No-Op function for when callable is required"""
    return None
