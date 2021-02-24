# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Testing helper functions for transforming dicts to DeliveryResponse models"""
from delivery_api_client import DeliveryResponse
from delivery_api_client import ExecuteResponse
from delivery_api_client import PrefetchResponse
from delivery_api_client import Option
from delivery_api_client import MboxResponse


def create_options(mbox):
    """Create Options"""
    if not mbox:
        return None

    result_options = []
    if mbox.get('options'):
        for _option in mbox.get('options'):
            option = Option(**_option)
            result_options.append(option)

    return result_options


def create_mboxes(mboxes):
    """Create list of MboxResponse objects"""
    if not mboxes:
        return None

    result_mboxes = []
    for mbox in mboxes:
        options = create_options(mbox)
        result_mboxes.append(MboxResponse(index=mbox.get("index"),
                                          name=mbox.get("name"),
                                          options=options))

    return result_mboxes


def create_prefetch_response(prefetch):
    """Create PrefetchResponse"""
    if not prefetch:
        return None

    mboxes = create_mboxes(prefetch.get('mboxes'))
    return PrefetchResponse(mboxes=mboxes)


def create_execute_response(execute):
    """Create ExecuteResponse"""
    if not execute:
        return None

    mboxes = create_mboxes(execute.get('mboxes'))
    return ExecuteResponse(mboxes=mboxes)


def create_delivery_response(response_dict):
    """Convert dict to DeliveryResponse instance"""
    execute_response = create_execute_response(response_dict.get('execute'))
    prefetch_response = create_prefetch_response(response_dict.get('prefetch'))
    delivery_response = DeliveryResponse(execute=execute_response, prefetch=prefetch_response)
    return delivery_response
