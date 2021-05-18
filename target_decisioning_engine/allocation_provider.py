# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Allocation provider"""
from target_decisioning_engine.constants import CAMPAIGN_BUCKET_SALT
from target_tools.utils import is_string
from target_tools.utils import create_uuid
from target_tools.hashing import hash_unencoded_chars
from target_tools.utils import memoize

TOTAL_BUCKETS = 10000
MAX_PERCENTAGE = 100


def valid_tnt_id(tnt_id=None):
    """
    :param tnt_id: (str) tntId
    :return: (str) tntId without the location hint
    """
    if tnt_id and is_string(tnt_id):
        return tnt_id.split(".")[0]
    return None


def get_or_create_visitor_id(visitor_id):
    """
    :param visitor_id: (delivery_api_client.Model.visitor_id.VisitorId) visitor ID object
    :return: (str) Returns visitor ID that will be used to compute the allocation
    """
    if not visitor_id:
        return create_uuid()

    return (
        visitor_id.marketing_cloud_visitor_id or
        valid_tnt_id(visitor_id.tnt_id) or
        visitor_id.third_party_id or
        create_uuid()
    )


def _calculate_allocation(device_id):
    """
    :param device_id: (str) device id based on visitorId, clientCode, campaignId and a salt value
    :return: (float) allocation value
    """
    signed_numeric_hash_value = hash_unencoded_chars(device_id)
    hash_fixed_bucket = abs(signed_numeric_hash_value) % TOTAL_BUCKETS
    allocation_value = (hash_fixed_bucket / float(TOTAL_BUCKETS)) * MAX_PERCENTAGE
    return round(allocation_value, 2)


calculate_allocation_memoized = memoize(_calculate_allocation)


def compute_allocation(client_id, activity_id, visitor_id, salt=CAMPAIGN_BUCKET_SALT):
    """
    :param client_id: (str) client ID
    :param activity_id: (str) activity ID
    :param visitor_id: (str | delivery_api_client.Model.visitor_id.VisitorId) visitor ID
    :param salt: (str) hashing salt
    :return: (float) allocation value
    """
    device_id = ".".join([
        client_id,
        str(activity_id),
        visitor_id if visitor_id and is_string(visitor_id) else get_or_create_visitor_id(visitor_id),
        salt
    ])
    return calculate_allocation_memoized(device_id)
