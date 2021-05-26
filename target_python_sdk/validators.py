# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Validation functions"""
from delivery_api_client import DeliveryRequest
from target_python_sdk.messages import MESSAGES
from target_tools.enums import DecisioningMethod


def validate_client_options(options):
    """Validates options for TargetClient"""
    if not options:
        return MESSAGES.get("OPTIONS_REQUIRED")

    client, organization_id, decisioning_method = \
        [options.get(k) for k in ("client", "organization_id", "decisioning_method")]

    if not client:
        return MESSAGES.get("CLIENT_REQUIRED")

    if not organization_id:
        return MESSAGES.get("ORG_ID_REQUIRED")

    if decisioning_method and decisioning_method not in [e.value for e in DecisioningMethod]:
        return MESSAGES.get("DECISIONING_METHOD_INVALID")

    return None


def validate_get_offers_options(options):
    """Validates options for get_offers"""
    if not options:
        return MESSAGES.get("OPTIONS_REQUIRED")

    request = options.get("request")
    if not request or not isinstance(request, DeliveryRequest):
        return MESSAGES.get("REQUEST_REQUIRED")

    execute = request.execute
    if execute and not execute.page_load \
            and not execute.mboxes:
        return MESSAGES.get("EXECUTE_FIELDS_REQUIRED")

    prefetch = request.prefetch
    if prefetch and not prefetch.page_load \
            and not prefetch.views \
            and not prefetch.mboxes:
        return MESSAGES.get("PREFETCH_FIELDS_REQUIRED")

    callback = options.get("callback")
    if callback and not callable(callback):
        return MESSAGES.get("INVALID_CALLBACK")

    return None


def validate_send_notifications_options(options):
    """Validates options for send_notifications"""
    if not options:
        return MESSAGES.get("OPTIONS_REQUIRED")

    request = options.get("request")
    if not request:
        return MESSAGES.get("REQUEST_REQUIRED")

    if not request.notifications and not request.telemetry:
        return MESSAGES.get("NOTIFICATIONS_REQUIRED")

    callback = options.get("callback")
    if callback and not callable(callback):
        return MESSAGES.get("INVALID_CALLBACK")

    return None
