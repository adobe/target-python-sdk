# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Assorted shared functions"""
import json

try:
    from functools import reduce
except ImportError:
    pass
import datetime
import operator
import uuid
import math
from tzlocal import get_localzone

EPOCH_START = datetime.datetime.utcfromtimestamp(0)
SECONDS_IN_MINUTE = 60


def compose_functions(outer, inner):
    """Compose two functions"""
    return lambda x: outer(inner(x))


def is_string(value):
    """Checks if value is string"""
    try:
        basestring
    except NameError:
        basestring = str
    return isinstance(value, basestring)


def is_number(value):
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


def create_visitor(config, visitor_cookie=None, customer_ids=None):
    """Create visitor"""
    print("{}.{}.{}".format(json.dumps(config), visitor_cookie, json.dumps(customer_ids)))
