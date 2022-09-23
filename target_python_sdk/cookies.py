# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Cookie related functions"""
import math
import time
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote
from target_tools.utils import is_int
from target_tools.utils import get_epoch_time_milliseconds
from target_tools.utils import parse_int
from target_tools.constants import MILLISECONDS_IN_SECOND

TARGET_COOKIE = "mbox"
SESSION_ID_COOKIE = "session"
DEVICE_ID_COOKIE = "PC"
LOCATION_HINT_COOKIE = "mboxEdgeCluster"


def create_internal_cookie(name, value, expires):
    """Create individual cookie to be stored inside Target cookie"""
    return {
        "name": name,
        "value": value,
        "expires": expires
    }


def get_internal_cookies(cookie_value):
    """Parse individual parts from cookie"""
    return cookie_value.split("|")


def deserialize_cookie(string):
    """Deserialize cookie"""
    parts = string.split("#")
    length = len(parts)

    if length == 0 or length < 3:
        return None

    if not is_int(parts[2]):
        return None

    return create_internal_cookie(
        unquote(parts[0]),
        unquote(parts[1]),
        parse_int(parts[2])
    )


def serialize_cookie(cookie):
    """Serialize cookie"""
    return "#".join([
        quote(cookie.get("name")),
        quote(cookie.get("value")),
        str(cookie.get("expires"))
    ])


def get_expires(cookie):
    """Get expiration time from cookie"""
    return cookie.get("expires")


def get_max_expires(cookies):
    """Get max expiration time from list of cookies"""
    return max([get_expires(cookie) for cookie in cookies])


def parse_cookies(target_cookie):
    """Deserializes single Target cookie into several individual cookies"""
    if not target_cookie:
        return {}

    raw_internal_cookies = get_internal_cookies(target_cookie)
    now_in_seconds = math.ceil(time.time())
    valid_cookies = [deserialized for deserialized in
                     (deserialize_cookie(cookie) for cookie in raw_internal_cookies) if
                     deserialized and now_in_seconds <= deserialized.get("expires")]
    return {cookie.get("name"): cookie for cookie in valid_cookies}


def create_target_cookie(cookies):
    """Serializes several individual cookies into a single Target cookie"""
    now = get_epoch_time_milliseconds()
    max_age = abs(get_max_expires(cookies) * MILLISECONDS_IN_SECOND - now)
    serialized_cookies = [serialize_cookie(cookie) for cookie in cookies]

    return {
        "name": TARGET_COOKIE,
        "value": "|".join(serialized_cookies),
        "maxAge": math.ceil(float(max_age) / MILLISECONDS_IN_SECOND)
    }
