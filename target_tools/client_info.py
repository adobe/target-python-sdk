# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Helper functions for deriving various info from client"""
import re

from target_python_sdk.utils import is_string
from target_python_sdk.utils import parse_int

BROWSER_MATCHERS_LIST = [
    {
        "name": "Edge",
        "regex": r"(edge|edgios|edga|edg)/((\d+)?[\w.]+)",
        "version_group_index": 2
    },
    {
        "name": "Mobile Safari",
        "regex": r"version/([\w.]+).+?mobile/\w+\s(safari)",
        "version_group_index": 1
    },
    {
        "name": "Safari",
        "regex": r"version/([\w.]+).+?(mobile\s?safari|safari)",
        "version_group_index": 1
    },
    {
        "name": "Chrome",
        "regex": r"(chrome)/v?([\w.]+)",
        "version_group_index": 2
    },
    {
        "name": "Firefox",
        "regex": r"(firefox)/([\w.-]+)$",
        "version_group_index": 2
    },
    {
        "name": "IE",
        "regex": r"(?:ms|\()(ie)\s([\w.]+)",
        "version_group_index": 2
    },
    {
        "name": "IE",
        "regex": r"(trident).+rv[:\s]([\w.]+).+like\sgecko",
        "version_group_index": 2,
        "version": 11
    }
]


def match_user_agent(matchers_list, process_func=None):
    """Use regex to match user agent
    :param matchers_list: (list<dict>) list of regex matchers
    :param process_func: (callable) match handler function
    :return: (any)
    """
    process_func = process_func if callable(process_func) else lambda matcher, _: matcher.get("name")

    def check_matches(user_agent):
        for matcher in matchers_list:
            pattern = re.compile(matcher.get("regex"), re.IGNORECASE)
            match = pattern.search(user_agent)
            if match:
                return process_func(matcher, match)

        return process_func({"name": "Unknown"}, None)

    return check_matches


def browser_from_user_agent(user_agent=None):
    """Use regex to determine browser from the user agent
    :param user_agent: (str) user agent
    :return: ({"name": str, "version": int})
    """
    if not user_agent:
        user_agent = ""

    def process_match(matcher, match=None):
        version = match.group(matcher.get("version_group_index")) if \
            match and len(match.groups()) >= matcher.get("version_group_index") else \
            matcher.get("version", "-1")

        major_version = parse_int(version.split(".")[0]) if is_string(version) else -1

        return {
            "name": matcher.get("name"),
            "version": major_version or -1
        }

    check_matches = match_user_agent(BROWSER_MATCHERS_LIST, process_match)
    return check_matches(user_agent)


def operating_system_from_user_agent(user_agent):
    """Get OS from user agent
    :param user_agent: (str) user agent
    :return: (str) OS name
    """
    check_matches = match_user_agent([
        {"name": "iOS", "regex": "iPhone|iPad|iPod"},
        {"name": "Android", "regex": "Android [0-9.]+;"},
        {"name": "Linux", "regex": " Linux "},
        {"name": "Unix", "regex": "FreeBSD|OpenBSD|CrOS"},
        {"name": "Windows", "regex": "[( ]Windows "},
        {"name": "Mac OS", "regex": "Macintosh;"}
    ])
    return check_matches(user_agent)


def device_type_from_user_agent(user_agent):
    """Gets device type from user agent
    :param user_agent: (str) browser user agent
    :return: (str) user device type
    """
    check_matches = match_user_agent([
        {"name": "iPod", "regex": "iPod"},
        {"name": "iPhone", "regex": "iPhone"},
        {"name": "iPad", "regex": "iPad"},
        {"name": "Nokia", "regex": "SymbOS|Maemo"},
        {"name": "Windows Phone", "regex": "IEMobile"},
        {"name": "Blackberry", "regex": "BlackBerry"},
        {"name": "Android", "regex": "Android [0-9.]+;"},
        {"name": "Desktop", "regex": ".*"}
    ])
    return check_matches(user_agent)
