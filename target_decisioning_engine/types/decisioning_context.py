# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""DecisioningContext model"""
from target_tools.types.limited_key_dict import LimitedKeyDict


class GeoContext(LimitedKeyDict):
    """GeoContext"""

    __key_map = {
        "country": "str",
        "region": "str",
        "city": "str",
        "latitude": "float",
        "longitude": "float"
    }

    def __init__(self, **kwargs):
        """kwargs should only consist of keys inside __key_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return GeoContext.__key_map.keys()


class UserContext(LimitedKeyDict):
    """UserContext"""

    __key_map = {
        "browserType": "str",
        "platform": "str",
        "locale": "str",
        "browserVersion": "int"
    }

    def __init__(self, **kwargs):
        """kwargs should only consist of keys inside __key_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return UserContext.__key_map.keys()


class PageContext(LimitedKeyDict):
    """PageContext"""

    __key_map = {
        "url": "str",
        "url_lc": "str",
        "path": "str",
        "path_lc": "str",
        "domain": "str",
        "domain_lc": "str",
        "subdomain": "str",
        "subdomain_lc": "str",
        "topLevelDomain": "str",
        "topLevelDomain_lc": "str",
        "query": "str",
        "query_lc": "str",
        "fragment": "str",
        "fragment_lc": "str"
    }

    def __init__(self, **kwargs):
        """kwargs should only consist of keys inside __key_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return PageContext.__key_map.keys()


class TimingContext(LimitedKeyDict):
    """TimingContext"""

    __key_map = {
        "current_timestamp": "int",
        "current_time": "str",
        "current_day": "str"
    }

    def __init__(self, **kwargs):
        """kwargs should only consist of keys inside __key_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return TimingContext.__key_map.keys()


class DecisioningContext(LimitedKeyDict):
    """DecisioningContext"""

    __key_map = {
        "allocation": "float",
        "current_timestamp": "int",
        "current_time": "str",
        "current_day": "str",
        "user": "UserContext",
        "page": "PageContext",
        "referring": "PageContext",
        "mbox": "dict",
        "geo": "GeoContext"
    }

    def __init__(self, **kwargs):
        """kwargs should only consist of keys inside __key_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return DecisioningContext.__key_map.keys()
