# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""DecisioningContext model"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-few-public-methods


class GeoContext:
    """GeoContext"""

    def __init__(self, country=None, region=None, city=None, latitude=None, longitude=None):
        self.country = country
        self.region = region
        self.city = city
        self.latitude = latitude
        self.longitude = longitude


class UserContext:
    """UserContext"""

    def __init__(self, browser_type=None, platform=None, locale=None, browser_version=None):
        self.browser_type = browser_type
        self.platform = platform
        self.locale = locale
        self.browser_version = browser_version


class PageContext:
    """PageContext"""

    def __init__(self, url=None, url_lc=None, path=None, path_lc=None, domain=None, domain_lc=None,
                 subdomain=None, subdomain_lc=None, top_level_domain=None, top_level_domain_lc=None,
                 query=None, query_lc=None, fragment=None, fragment_lc=None):
        self.url = url
        self.url_lc = url_lc
        self.path = path
        self.path_lc = path_lc
        self.domain = domain
        self.domain_lc = domain_lc
        self.subdomain = subdomain
        self.subdomain_lc = subdomain_lc
        self.top_level_domain = top_level_domain
        self.top_level_domain_lc = top_level_domain_lc
        self.query = query
        self.query_lc = query_lc
        self.fragment = fragment
        self.fragment_lc = fragment_lc


class TimingContext:
    """TimingContext"""

    def __init__(self, current_timestamp=None, current_time=None, current_day=None):
        self.current_timestamp = current_timestamp
        self.current_time = current_time
        self.current_day = current_day


class DecisioningContext:
    """DecisioningContext"""

    def __init__(self, allocation=None, current_timestamp=None, current_time=None, current_day=None,
                 user=None, page=None, referring=None, mbox=None, geo=None):
        self.allocation = allocation
        self.current_timestamp = current_timestamp
        self.current_time = current_time
        self.current_day = current_day
        self.user = user
        self.page = page
        self.referring = referring
        self.mbox = mbox
        self.geo = geo
