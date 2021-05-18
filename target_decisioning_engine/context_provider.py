# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""On Device Decisioning Context Provider"""
import datetime

from delivery_api_client import ChannelType
from delivery_api_client import Context
from target_decisioning_engine.types.decisioning_context import UserContext
from target_decisioning_engine.types.decisioning_context import PageContext
from target_decisioning_engine.types.decisioning_context import GeoContext
from target_decisioning_engine.types.decisioning_context import DecisioningContext
from target_decisioning_engine.types.decisioning_context import TimingContext
from target_decisioning_engine.utils import parse_url
from target_tools.utils import is_string
from target_tools.utils import get_epoch_time_milliseconds
from target_tools.client_info import browser_from_user_agent
from target_tools.client_info import operating_system_from_user_agent

EMPTY_CONTEXT = Context(channel=ChannelType.WEB)


def get_lower_case_attributes(obj):
    """Put lowercase versions of object attributes onto the object
    :param obj: (dict) dict to traverse, required
    :return: (dict) new dict with lowercase versions of all the string attributes from original dict
    """
    result = {}
    for key in obj.keys():
        result["{}_lc".format(key)] = obj[key].lower() if is_string(obj[key]) else obj[key]
    return result


def _create_browser_context(context):
    """Create browser/user context
    :param context: (delivery_api_client.Model.context.Context) Delivery API context
    :return: (target_decisioning_engine.types.decisioning_context.UserContext) User context
    """
    user_agent = context.user_agent or ""
    browser = browser_from_user_agent(user_agent)
    platform = operating_system_from_user_agent(user_agent)

    return UserContext(browserType=browser.get("name", "").lower(),
                       platform=platform,
                       locale="en",
                       browserVersion=browser.get("version")
                       )


def _create_url_context(url):
    """Create URL context
    :param url: (str) URL
    :return: (target_decisioning_engine.types.decisioning_context.PageContext) Page context
    """
    if not url or not is_string(url):
        url = ""

    url_attributes = parse_url(url)
    lc_attributes = get_lower_case_attributes(url_attributes)
    url_attributes.update(lc_attributes)

    return PageContext(**url_attributes)


def create_page_context(address):
    """Create page context from address url
    :param address: (delivery_api_client.Model.address.Address) Delivery API address
    :return: (target_decisioning_engine.types.decisioning_context.PageContext) Page context
    """
    return _create_url_context(address.url if address else "")


def create_referring_context(address):
    """Create page context from address referring url
    :param address: (delivery_api_client.Model.address.Address) Delivery API address
    :return: (target_decisioning_engine.types.decisioning_context.PageContext) Page context
    """
    return _create_url_context(address.referring_url if address else "")


def create_mbox_context(mbox_request):
    """Create mbox context
    :param mbox_request: (delivery_api_client.Model.mbox_request.MboxRequest) Delivery API mbox request
    :return: (dict) Mbox context
    """
    if not mbox_request:
        return {}

    parameters = mbox_request.parameters or {}
    lc_parameters = get_lower_case_attributes(parameters)
    parameters.update(lc_parameters)
    return parameters


def create_geo_context(_geo=None):
    """Create geo context
    :param _geo: (delivery_api_client.Model.geo.Geo) Delivery API geo
    :return: (target_decisioning_engine.types.decisioning_context.GeoContext) Geo context
    """
    if not _geo:
        return GeoContext()

    return GeoContext(country=_geo.country_code,
                      region=_geo.state_code,
                      city=_geo.city,
                      latitude=_geo.latitude,
                      longitude=_geo.longitude
                      )


def two_digit_string(_value):
    """Convert an int value to a fixed 2-digit string
    :param _value: (int) integer value to convert to string
    :return: (str) 2-digit string
    """
    return "0{}".format(_value) if _value < 10 else str(_value)


def _create_timing_context():
    """Create timing context
    :return: (target_decisioning_engine.types.decisioning_context.TimingContext) Timing context
    """
    now = datetime.datetime.utcnow()
    current_hours = two_digit_string(now.hour)
    current_minutes = two_digit_string(now.minute)
    _current_time = "{}{}".format(current_hours, current_minutes)  # 24-hour time, UTC, HHmm
    # now.weekday() gives us Monday as 0 through Sunday as 6.  We want to return Monday as 1 through Sunday as 7
    _current_day = now.weekday() + 1
    return TimingContext(current_timestamp=get_epoch_time_milliseconds(now),
                         current_time=_current_time,
                         current_day=_current_day)


def create_decisioning_context(delivery_request):
    """Create decisioning context
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest) Delivery API request
    :return: (target_decisioning_engine.types.decisioning_context.DecisioningContext) Decisioning context
    """
    context = delivery_request.context or EMPTY_CONTEXT

    timing_context = _create_timing_context()

    return DecisioningContext(current_timestamp=timing_context.get("current_timestamp"),
                              current_time=timing_context.get("current_time"),
                              current_day=timing_context.get("current_day"),
                              user=_create_browser_context(context),
                              page=create_page_context(context.address),
                              referring=create_referring_context(context.address),
                              geo=create_geo_context(context.geo)
                              )
