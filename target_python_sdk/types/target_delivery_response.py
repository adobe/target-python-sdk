# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""TargetDeliveryResponse"""
from target_tools.types.limited_key_dict import LimitedKeyDict


class TargetDeliveryResponse(LimitedKeyDict):
    """TargetDeliveryResponse"""

    __key_map = {
        "target_cookie": "dict",
        "target_location_hint_cookie": "dict",
        "analytics_details": "list<delivery_api_client.Model.analytics_response.AnalyticsResponse>",
        "trace": "list<dict<str, object>>",
        "response_tokens": "list<dict<str, object>>",
        "meta": "dict",
        "response": "delivery_api_client.Model.delivery_response.DeliveryResponse"
    }

    def __init__(self, **kwargs):
        """kwargs should only consist of keys inside __key_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return TargetDeliveryResponse.__key_map.keys()
