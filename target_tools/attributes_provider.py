# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""AttributesProvider"""

from target_python_sdk.utils import is_list
from target_tools.messages import attribute_not_exist
from target_tools.constants import REQUEST_TYPES

def create_indexed(response):
    """
    :param response: (delivery_api_client.Model.delivery_response.DeliveryResponse)
        Target View Delivery API response
    """
    result = {}
    for request_type in REQUEST_TYPES:
        if response.request_type and response.request_type.get(
                'mboxes') and is_list(response.request_type.get('mboxes')):
            for mbox in response.request_type.get('mboxes'):
                name = mbox.get('name')
                for option in mbox.get('options'):
                    if option.get('content_type') == "json" and option.get(
                            'content'):
                        result[name] = {} if not result or not result.get(
                            name) else result[name]
                        result[name].update(option.get('content'))
    return result


class AttributesProvider:
    """AttributesProvider"""

    def __init__(self, offers_response):
        """
        :param offers_response: (TargetDeliveryResponse)
        """
        self.offers_response = offers_response
        self.indexed = create_indexed(offers_response.response) if offers_response and offers_response.response else {}

    def get_value(self, mbox_name, key):
        """
        Gets value
        :param mbox_name: (str) The specified mbox name
        """
        if mbox_name not in self.indexed or key not in self.indexed.get(
                mbox_name):
            raise Exception(attribute_not_exist(key, mbox_name))
        return self.indexed.get(mbox_name).get(key)

    def get_as_object(self, mbox_name=None):
        """Gets object"""
        return self.indexed.get(mbox_name) if mbox_name else self.indexed

    def as_object(self, mbox_name=None):
        """Gets object"""
        return self.get_as_object(mbox_name)

    def to_json(self):
        """Gets json"""
        return self.get_as_object(None)

    def get_response(self):
        """Gets response"""
        return self.offers_response
