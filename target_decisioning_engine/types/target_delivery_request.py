# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""TargetDeliveryRequest model"""


class TargetDeliveryRequest:
    """TargetDeliveryRequest"""

    def __init__(self, request, target_cookie=None, target_location_hint=None,
                 consumer_id=None, customer_ids=None, session_id=None, visitor=None, trace=None):
        """
        :param request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
            Target View Delivery API request, required
        :param target_cookie: (str) Target cookie, optional
        :param target_location_hint: (str) Target Location Hint, optional
        :param consumer_id: (str) When stitching multiple calls, different consumerIds should be provided, optional
        :param customer_ids: (list) A list of Customer Ids in VisitorId-compatible format, optional
        :param session_id: (str) Session Id, used for linking multiple requests, optional
        :param visitor: (dict) Supply an external VisitorId instance, optional
        :param trace: (delivery_api_client.Model.trace.Trace) Target trace, optional
        """
        self.request = request
        self.target_cookie = target_cookie
        self.target_location_hint = target_location_hint
        self.consumer_id = consumer_id
        self.customer_ids = customer_ids
        self.session_id = session_id
        self.visitor = visitor
        self.trace = trace
