# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""AttributesProvider"""
from delivery_api_client import OptionType
from target_tools.messages import attribute_not_exist
from target_tools.constants import REQUEST_TYPES


def create_indexed(response):
    """
    :param response: (delivery_api_client.Model.delivery_response.DeliveryResponse)
        Target View Delivery API response
    :return (dict<str, str|dict|list>) returns a map of mbox names to content
    """
    result = {}
    for request_type in REQUEST_TYPES:
        if getattr(response, request_type) and getattr(response, request_type).mboxes:
            for mbox in getattr(response, request_type).mboxes:
                name = mbox.name
                for option in mbox.options:
                    if option.type == OptionType.JSON and option.content:
                        result[name] = {} if not result or not result.get(
                            name) else result[name]
                        result[name].update(option.content)
    return result


class AttributesProvider:
    """AttributesProvider"""

    def __init__(self, offers_response):
        """
        :param offers_response: (dict) get_offers response
        """
        self.offers_response = offers_response
        self.indexed = {}
        if offers_response and offers_response.get("response"):
            self.indexed = create_indexed(offers_response.get("response"))

    def get_value(self, mbox_name, key):
        """
        Gets value
        :param mbox_name: (str) The specified mbox name
        :param key: (str) Content dict key for the mbox content - if content is a dict
        """
        if mbox_name not in self.indexed or key not in self.indexed.get(
                mbox_name):
            raise Exception(attribute_not_exist(key, mbox_name))
        return self.indexed.get(mbox_name).get(key)

    def as_object(self, mbox_name=None):
        """Gets object based on mbox name
        :param mbox_name: (str) mbox name, optional
        :return: (str|dict|list) returns single mbox content if mbox_name provided, else entire mbox content map
        """
        return self.indexed.get(mbox_name) if mbox_name else self.indexed

    def get_response(self):
        """
        :return (dict) returns get_offers response
        """
        return self.offers_response


def get_attributes_callback(get_offers_resp):
    """Callback fn for when get_attributes is called asynchronously"""
    return AttributesProvider(get_offers_resp)
