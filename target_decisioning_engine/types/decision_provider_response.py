# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Response model for DecisionProvider"""
from delivery_api_client import DeliveryResponse


class DecisionProviderResponse(DeliveryResponse):
    """Child class for DeliveryResponse which includes ODD-specific attributes"""

    def __init__(self, remote_mboxes=None, remote_views=None, status=None, request_id=None, _id=None,
                 client=None, edge_host=None, execute=None, prefetch=None):
        DeliveryResponse.__init__(self, status=status, request_id=request_id, id=_id, client=client,
                                  edge_host=edge_host,
                                  execute=execute, prefetch=prefetch)
        self.remote_mboxes = remote_mboxes
        self.remote_views = remote_views
