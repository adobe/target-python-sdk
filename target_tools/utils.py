# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Assorted utility functions for target_tools package"""
try:
    from functools import reduce
except ImportError:
    pass
import datetime
import operator
import uuid
import math
from six import string_types
from tzlocal import get_localzone
from delivery_api_client import ModelProperty as Property
from delivery_api_client import ExecuteRequest
from delivery_api_client import PrefetchRequest
from delivery_api_client import MboxRequest
from target_tools.constants import MILLISECONDS_IN_SECOND
from target_tools.constants import REQUEST_TYPES
from target_tools.enums import DecisioningMethod
from target_tools.logger import get_logger
from target_tools.messages import property_token_mismatch


EPOCH_START = datetime.datetime.utcfromtimestamp(0)
SECONDS_IN_MINUTE = 60

MBOXES = "mboxes"

REQUEST_TYPE_MAP = {
    "execute": ExecuteRequest,
    "prefetch": PrefetchRequest
}

VIEWS = "views"
MBOXES = "mboxes"

logger = get_logger()


def requires_decisioning_engine(decisioning_method):
    """Determines if any decisioning is done on-device or not"""
    return decisioning_method in [DecisioningMethod.ON_DEVICE.value, DecisioningMethod.HYBRID.value]


def get_property_token(_property=None):
    """Get property token"""
    return _property.token if _property else None


def get_property(config, request):
    """Attempts to fetch property token from request and falls back to config"""
    if not config:
        config = {}

    config_property_token = config.get("property_token")
    request_property_token = get_property_token(request._property) if request else None
    property_token = request_property_token or config_property_token

    if request_property_token and request_property_token != config_property_token:
        logger.debug(
            property_token_mismatch(request_property_token, config_property_token)
        )

    return Property(token=property_token) if property_token else None


def decisioning_engine_ready(decisioning_engine):
    """Checks if decisioning engine is ready"""
    return decisioning_engine if decisioning_engine and decisioning_engine.is_ready() else None


def has_requested(items_key, delivery_request):
    """
    :param items_key: ("mboxes"|"views") key, required
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target Delivery API request, required
    :return: (bool) Does request include items_key
    """
    for _type in REQUEST_TYPES:
        if delivery_request and getattr(delivery_request, _type, None) \
                and getattr(getattr(delivery_request, _type, {}), items_key, None):
            return True
    return False


def has_requested_views(delivery_request):
    """
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target Delivery API request, required
    :return: (bool) Does request include views
    """
    return has_requested(VIEWS, delivery_request)


def get_names_for_requested(items_key, delivery_request):
    """
    :param items_key: ("mboxes" | "views")
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target View Delivery API request, required
    :return (set) Set of mbox names
    """
    result_set = set()
    for request_type in REQUEST_TYPES:
        request_item = getattr(delivery_request, request_type)
        if not request_item:
            continue
        items = getattr(request_item, items_key, []) or []
        for item in (item for item in items if item and item.name):
            result_set.add(item.name)
    return result_set


def get_mbox_names(delivery_request):
    """
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target Delivery API request, required
    :return: (set<str>) Set of mbox names
    """
    return get_names_for_requested(MBOXES, delivery_request)


def add_mboxes_to_request(mbox_names, request, request_type="execute"):
    """Modifies request in place to add specified mboxes
    :param mbox_names: (list) A list of mbox names that contain JSON content attributes, required
    :param request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target View Delivery API request, required
    :param request_type: ("execute"|"prefetch")
    """
    requested_mboxes = get_mbox_names(request)
    mboxes = []
    if not getattr(request, request_type):
        subreq_instance = REQUEST_TYPE_MAP.get(request_type)()
        setattr(request, request_type, subreq_instance)

    subreq = getattr(request, request_type)
    if subreq.mboxes:
        mboxes.extend(subreq.mboxes)

    highest_user_specified_index_mbox = max(
        mboxes, key=lambda mbox: mbox.index).index if mboxes else 0

    next_index = highest_user_specified_index_mbox + 1

    for mbox_name in (name for name in mbox_names if name not in requested_mboxes):
        mboxes.append(MboxRequest(name=mbox_name, index=next_index))
        next_index += 1

    subreq.mboxes = mboxes

    return request


def get_view_names(delivery_request):
    """
    :param delivery_request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
        Target Delivery API request, required
    :return: (set<str>) Set of view names
    """
    return get_names_for_requested(VIEWS, delivery_request)


def noop(*args, **kwargs):
    """No-Op function for when callable is required"""
    return None


def memoize(func, args_resolver=None):
    """Function memoization for better performance"""
    cache = dict()

    def memoized_func(*args, **kwargs):
        key = args_resolver(args, kwargs) if args_resolver else (args, frozenset(kwargs.items()))
        if key in cache:
            return cache[key]
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    return memoized_func


def compose_functions(outer, inner):
    """Compose two functions"""
    return lambda x: outer(inner(x))


def is_string(value):
    """Checks if value is string"""
    return isinstance(value, string_types)


def is_int(value):
    """Checks if value is numeric"""
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def parse_int(value):
    """Casts value to integer if possible, otherwise returns None"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def parse_float(value):
    """Casts value to float if possible, otherwise returns None"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def is_dict(value):
    """Checks if value is a dict"""
    return isinstance(value, dict)


def is_list(value):
    """Checks if value is a list"""
    return isinstance(value, list)


def create_uuid():
    """Create new UUID"""
    return str(uuid.uuid4())


def get_epoch_time(utc_datetime=None):
    """Get epoch time (seconds) from either passed in UTC datetime or current datetime"""
    if not utc_datetime:
        utc_datetime = datetime.datetime.utcnow()
    return math.ceil((utc_datetime - EPOCH_START).total_seconds())


def get_epoch_time_milliseconds(utc_datetime=None):
    """Get epoch time (milliseconds) from either passed in UTC datetime or current datetime"""
    epoch_seconds = get_epoch_time(utc_datetime)
    return epoch_seconds * MILLISECONDS_IN_SECOND


def get_timezone_offset():
    """Get local timezone offset from UTC"""
    timezone = get_localzone()
    offset_minutes = timezone.utcoffset(datetime.datetime.now()).total_seconds() // SECONDS_IN_MINUTE
    return parse_int(offset_minutes)


def flatten_list(_list):
    """Flatten list with nested lists"""
    if not _list:
        return []
    return reduce(operator.add, _list)


def remove_empty_values(_dict):
    """Removes Nonetype dict values"""
    return {k: v for k, v in list(_dict.items()) if v is not None}


def is_empty(val):
    """Returns True if val is Falsy, otherwise returns False"""
    return not bool(val)


def to_dict(obj):
    """Converts a class instance object into a dict"""
    if isinstance(obj, dict):
        data = {}
        for (key, val) in obj.items():
            data[key] = to_dict(val)
        return data
    if hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(v) for v in obj]
    if hasattr(obj, "attribute_map"):
        data = {}
        for key, mapped_key in obj.attribute_map.items():
            value = getattr(obj, key)
            data[mapped_key] = to_dict(value)
        return data
    if hasattr(obj, "__dict__"):
        return {key: to_dict(value) for key, value in obj.__dict__.items()}
    return obj


def get_value_from_object(obj, key):
    """Retrieves value via key for dicts or attribute for instance objects"""
    if is_dict(obj):
        return obj.get(key)
    return getattr(obj, key, None)
