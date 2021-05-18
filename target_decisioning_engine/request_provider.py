# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""DeliveryRequest validation and helper functions"""
from copy import deepcopy
from delivery_api_client import AuthenticatedState
from delivery_api_client import VisitorId
from delivery_api_client import Context
from delivery_api_client import Geo
from target_tools.utils import is_list
from target_tools.utils import is_string
from target_tools.utils import create_uuid


def get_customer_id(visitor_id):
    """
    :param visitor_id: (delivery_api_client.Model.visitor_id.VisitorId) visitor ID object
    :return: (str) first non-blank marketingCloudVisitorId, tntId, thirdPartyId
    """
    if not visitor_id.customer_ids or not is_list(visitor_id.customer_ids):
        return None

    customer_ids = [customer_id for customer_id in visitor_id.customer_ids if
                    customer_id.authenticated_state == AuthenticatedState.AUTHENTICATED]

    return customer_ids[0].id if customer_ids else None


def _no_ids(visitor_id):
    """
    :param visitor_id: (delivery_api_client.Model.visitor_id.VisitorId) visitor ID object
    :return: (bool) True if at least one type of id exists on visitor_id object
    """
    return (not visitor_id.tnt_id and not visitor_id.marketing_cloud_visitor_id
            and not get_customer_id(visitor_id) and not visitor_id.third_party_id)


def valid_visitor_id(visitor_id, target_location_hint):
    """
    :param visitor_id: (delivery_api_client.Model.visitor_id.VisitorId) visitor ID object
    :param target_location_hint: (str) Target location hint
    :return: (delivery_api_client.Model.visitor_id.VisitorId) updated copy of visitor ID object
    """
    result = deepcopy(visitor_id) if visitor_id else VisitorId()

    if _no_ids(result):
        location_hint = ".{}_0".format(target_location_hint) if target_location_hint \
                                                                and is_string(target_location_hint) else ""
        result.tnt_id = "{}{}".format(create_uuid(), location_hint)
    return result


def valid_delivery_request(request, target_location_hint, valid_geo_request_context):
    """
    :param request: (delivery_api_client.Model.delivery_request.DeliveryRequest) request
    :param target_location_hint: (str) Target location hint
    :param valid_geo_request_context: (callable) function that checks if request geo is valid
    :return: (delivery_api_client.Model.delivery_request.DeliveryRequest) updated copy of request
    """
    request_copy = deepcopy(request)
    context = request_copy.context or Context()
    context.geo = valid_geo_request_context(context.geo or Geo())
    request_copy.context = context
    request_copy.id = valid_visitor_id(request_copy.id, target_location_hint)
    request_copy.request_id = request_copy.request_id or create_uuid()
    return request_copy
