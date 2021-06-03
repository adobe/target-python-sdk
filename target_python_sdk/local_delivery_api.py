# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""LocalDeliveryApi for ODD"""
from target_decisioning_engine.types.target_delivery_request import TargetDeliveryRequest
from target_tools.messages import DECISIONING_ENGINE_NOT_READY


class LocalDeliveryApi:
    """LocalDeliveryApi - used for on-device-decisioning instead of DeliveryApi"""

    def __init__(self, decisioning_engine, visitor, target_location_hint):
        self.decisioning_engine = decisioning_engine
        self.visitor = visitor
        self.target_location_hint = target_location_hint

    def execute(self, ims_org_id, session_id, delivery_request, **kwargs):
        """Local execution of get_offers"""
        if not self.decisioning_engine:
            raise Exception(DECISIONING_ENGINE_NOT_READY)

        get_offers_options = TargetDeliveryRequest(target_location_hint=self.target_location_hint,
                                                   request=delivery_request,
                                                   session_id=session_id,
                                                   visitor=self.visitor)
        return self.decisioning_engine.get_offers(get_offers_options)
