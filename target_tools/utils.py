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


def add_mboxes_to_request(mbox_names, request, request_type):
    """The add_mboxes_to_request method
    Ensures the mboxes specified are part of the returned delivery request
    :parameter
    mbox_names: list<str> - A list of mbox names that contains JSON content attributes, required
    request: "import("../delivery-api-client/models/DeliveryRequest").DeliveryRequest" - Target View
        Delivery API request, required
    request_type: str ('execute'|'prefetch')
    """
    print(mbox_names, request, request_type)
    return request
>>>>>>> TNT-38924 getAttributes()
