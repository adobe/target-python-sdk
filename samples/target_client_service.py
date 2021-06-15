# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
import asyncio

from delivery_api_client import DeliveryRequest
from delivery_api_client import ExecuteRequest
from delivery_api_client import PrefetchRequest
from delivery_api_client import RequestDetails
from delivery_api_client import CustomerId
from delivery_api_client import AuthenticatedState
from samples.target_request_utils import get_context
from samples.target_request_utils import get_visitor_id


def _get_prefetch_views_request(http_request, get_offers_options, views, request_id=None):
    context = get_context(http_request)
    visitor_id = get_visitor_id(http_request)
    prefetch_request = PrefetchRequest(views=views)
    delivery_request = DeliveryRequest(id=visitor_id,
                                       context=context,
                                       request_id=request_id,
                                       prefetch=prefetch_request)
    get_offers_options["request"] = delivery_request

    user_id = CustomerId(id="67312378756723456", integration_code="userid",
                         authenticated_state=AuthenticatedState.AUTHENTICATED)
    puuid = CustomerId(id="550e8400-e29b-41d4-a716-446655440000", integration_code="puuid",
                       authenticated_state=AuthenticatedState.UNKNOWN)
    get_offers_options["customer_ids"] = [user_id, puuid]
    return get_offers_options


class TargetClientService:

    def __init__(self, target_client):
        self.target_client = target_client

    def get_page_load_target_delivery_response(self, http_request, get_offers_options):
        context = get_context(http_request)
        visitor_id = get_visitor_id(http_request)
        page_load_request = ExecuteRequest(page_load=RequestDetails())
        delivery_request = DeliveryRequest(id=visitor_id,
                                           context=context,
                                           execute=page_load_request)
        get_offers_options["request"] = delivery_request

        return self.target_client.get_offers(get_offers_options)

    def get_mbox_target_delivery_response(self, http_request, get_offers_options,
                                          execute_mboxes=None, prefetch_mboxes=None):
        if not execute_mboxes and not prefetch_mboxes:
            return None

        context = get_context(http_request)
        visitor_id = get_visitor_id(http_request)
        execute_request = ExecuteRequest(mboxes=execute_mboxes) if execute_mboxes else None
        prefetch_request = PrefetchRequest(mboxes=prefetch_mboxes) if prefetch_mboxes else None
        delivery_request = DeliveryRequest(id=visitor_id,
                                           context=context,
                                           execute=execute_request,
                                           prefetch=prefetch_request)
        get_offers_options["request"] = delivery_request
        return self.target_client.get_offers(get_offers_options)

    def prefetch_views_target_delivery_response(self, http_request, request_id, get_offers_options, views):
        get_offers_options = _get_prefetch_views_request(http_request, get_offers_options, views, request_id=request_id)
        return self.target_client.get_offers(get_offers_options)

    # For use with Python 3.9+/asyncio
    async def prefetch_views_target_delivery_response_asyncio(self, http_request, request_id, get_offers_options,
                                                              views):
        get_offers_options = _get_prefetch_views_request(http_request, get_offers_options, views, request_id=request_id)
        return await asyncio.to_thread(self.target_client.get_offers, get_offers_options)

    def send_notifications(self, http_request, get_offers_options, notifications):
        context = get_context(http_request)
        visitor_id = get_visitor_id(http_request)
        delivery_request = DeliveryRequest(id=visitor_id,
                                           context=context,
                                           notifications=notifications)
        get_offers_options["request"] = delivery_request
        return self.target_client.send_notifications(get_offers_options)
