# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Unit tests for target_decisioning_engine.context_provider module"""
import unittest

from delivery_api_client import Context
from delivery_api_client import ChannelType
from delivery_api_client import Address
from delivery_api_client import MboxRequest
from delivery_api_client import Geo
from delivery_api_client import DeliveryRequest
from target_decisioning_engine.context_provider import create_page_context
from target_decisioning_engine.context_provider import create_referring_context
from target_decisioning_engine.context_provider import create_mbox_context
from target_decisioning_engine.context_provider import create_geo_context
from target_decisioning_engine.context_provider import create_decisioning_context
from target_decisioning_engine.types.decisioning_context import UserContext
from target_decisioning_engine.types.decisioning_context import PageContext
from target_decisioning_engine.types.decisioning_context import GeoContext
from target_decisioning_engine.types.decisioning_context import DecisioningContext
from target_tools.constants import EMPTY_STRING

FIREFOX_USER_AGENT = \
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"

TEST_URL = "http://Blog.Myfavesite.GeoCities.com/Posts?Page=1#Bottom"


class TestContextProvider(unittest.TestCase):

    def test_create_browser_context(self):
        request_context = Context(channel=ChannelType.WEB, user_agent=FIREFOX_USER_AGENT)
        request = DeliveryRequest(context=request_context)

        result = create_decisioning_context(request)

        self.assertTrue(isinstance(result.user, UserContext))
        self.assertEqual(result.user.browser_type, "firefox")
        self.assertEqual(result.user.platform, "Windows")
        self.assertEqual(result.user.locale, "en")
        self.assertEqual(result.user.browser_version, 47)

    def test_create_page_context_url_empty_string(self):
        address = Address(url=EMPTY_STRING)
        result = create_page_context(address)

        self.assertTrue(isinstance(result, PageContext))
        for attribute in result.__dict__.values():
            self.assertEqual(attribute, EMPTY_STRING)

    def test_create_page_context_non_empty_url(self):
        address = Address(url=TEST_URL)
        result = create_page_context(address)

        self.assertTrue(isinstance(result, PageContext))
        self.assertEqual(result.domain, "Blog.Myfavesite.GeoCities.com")
        self.assertEqual(result.domain_lc, "blog.myfavesite.geocities.com")
        self.assertEqual(result.fragment, "Bottom")
        self.assertEqual(result.fragment_lc, "bottom")
        self.assertEqual(result.path, "/Posts")
        self.assertEqual(result.path_lc, "/posts")
        self.assertEqual(result.query, "Page=1")
        self.assertEqual(result.query_lc, "page=1")
        self.assertEqual(result.subdomain, "Blog")
        self.assertEqual(result.subdomain_lc, "blog")
        self.assertEqual(result.top_level_domain, "GeoCities.com")
        self.assertEqual(result.top_level_domain_lc, "geocities.com")
        self.assertEqual(result.url, "http://Blog.Myfavesite.GeoCities.com/Posts?Page=1#Bottom")
        self.assertEqual(result.url_lc, "http://blog.myfavesite.geocities.com/posts?page=1#bottom")

    def test_create_page_context_applookout(self):
        address = Address(url="https://stage.applookout.net/")
        result = create_page_context(address)

        self.assertTrue(isinstance(result, PageContext))
        self.assertEqual(result.domain, "stage.applookout.net")
        self.assertEqual(result.domain_lc, "stage.applookout.net")
        self.assertEqual(result.fragment, "")
        self.assertEqual(result.fragment_lc, "")
        self.assertEqual(result.path, "/")
        self.assertEqual(result.path_lc, "/")
        self.assertEqual(result.query, "")
        self.assertEqual(result.query_lc, "")
        self.assertEqual(result.subdomain, "stage")
        self.assertEqual(result.subdomain_lc, "stage")
        self.assertEqual(result.top_level_domain, "net")
        self.assertEqual(result.top_level_domain_lc, "net")
        self.assertEqual(result.url, "https://stage.applookout.net/")
        self.assertEqual(result.url_lc, "https://stage.applookout.net/")

    def test_create_referring_context_url_empty_string(self):
        address = Address(referring_url=EMPTY_STRING)
        result = create_referring_context(address)

        self.assertTrue(isinstance(result, PageContext))
        for attribute in result.__dict__.values():
            self.assertEqual(attribute, EMPTY_STRING)

    def test_create_referring_context_non_empty_url(self):
        address = Address(referring_url=TEST_URL)
        result = create_referring_context(address)

        self.assertTrue(isinstance(result, PageContext))
        self.assertEqual(result.domain, "Blog.Myfavesite.GeoCities.com")
        self.assertEqual(result.domain_lc, "blog.myfavesite.geocities.com")
        self.assertEqual(result.fragment, "Bottom")
        self.assertEqual(result.fragment_lc, "bottom")
        self.assertEqual(result.path, "/Posts")
        self.assertEqual(result.path_lc, "/posts")
        self.assertEqual(result.query, "Page=1")
        self.assertEqual(result.query_lc, "page=1")
        self.assertEqual(result.subdomain, "Blog")
        self.assertEqual(result.subdomain_lc, "blog")
        self.assertEqual(result.top_level_domain, "GeoCities.com")
        self.assertEqual(result.top_level_domain_lc, "geocities.com")
        self.assertEqual(result.url, "http://Blog.Myfavesite.GeoCities.com/Posts?Page=1#Bottom")
        self.assertEqual(result.url_lc, "http://blog.myfavesite.geocities.com/posts?page=1#bottom")

    def test_create_mbox_context(self):
        params = {
            "a": "FirstParam",
            "b": "SecondOne",
            "c": "third"
        }
        mbox = MboxRequest(parameters=params)
        result = create_mbox_context(mbox)
        self.assertEqual(result.get("a"), "FirstParam")
        self.assertEqual(result.get("b"), "SecondOne")
        self.assertEqual(result.get("c"), "third")
        self.assertEqual(result.get("a_lc"), "firstparam")
        self.assertEqual(result.get("b_lc"), "secondone")
        self.assertEqual(result.get("c_lc"), "third")

    def test_create_geo_context_no_geo(self):
        result = create_geo_context(None)
        for val in result.__dict__.values():
            self.assertEqual(val, None)

    def test_create_geo_context(self):
        geo = Geo(country_code="US",
                  state_code="CA",
                  city="San Francisco",
                  latitude=38.8,
                  longitude=-77.0
                  )
        result = create_geo_context(geo)

        self.assertTrue(isinstance(result, GeoContext))
        self.assertEqual(result.country, "US")
        self.assertEqual(result.region, "CA")
        self.assertEqual(result.city, "San Francisco")
        self.assertEqual(result.latitude, 38.8)
        self.assertEqual(result.longitude, -77.0)

    def test_create_timing_context(self):
        request_context = Context(ChannelType.WEB)
        request = DeliveryRequest(context=request_context)

        result = create_decisioning_context(request)

        self.assertTrue(result.current_day > 0)
        self.assertTrue(result.current_day < 8)
        self.assertEqual(len(result.current_time), 4)
        self.assertTrue(result.current_timestamp > 0)

    def test_create_decisioning_context_generate_blank_context(self):
        request_context = Context(ChannelType.WEB)
        request = DeliveryRequest(context=request_context)

        result = create_decisioning_context(request)

        self.assertTrue(isinstance(result, DecisioningContext))
        # timing
        self.assertIsNotNone(result.current_time)
        self.assertIsNotNone(result.current_timestamp)
        self.assertIsNotNone(result.current_day)
        # geo
        self.assertIsNone(result.geo.latitude)
        self.assertIsNone(result.geo.longitude)
        self.assertIsNone(result.geo.country)
        self.assertIsNone(result.geo.region)
        self.assertIsNone(result.geo.city)
        # page
        self.assertEqual(result.page.domain, "")
        self.assertEqual(result.page.domain_lc, "")
        self.assertEqual(result.page.fragment, "")
        self.assertEqual(result.page.fragment_lc, "")
        self.assertEqual(result.page.path, "")
        self.assertEqual(result.page.path_lc, "")
        self.assertEqual(result.page.query, "")
        self.assertEqual(result.page.query_lc, "")
        self.assertEqual(result.page.subdomain, "")
        self.assertEqual(result.page.subdomain_lc, "")
        self.assertEqual(result.page.top_level_domain, "")
        self.assertEqual(result.page.top_level_domain_lc, "")
        self.assertEqual(result.page.url, "")
        self.assertEqual(result.page.url_lc, "")
        # referring
        self.assertEqual(result.referring.domain, "")
        self.assertEqual(result.referring.domain_lc, "")
        self.assertEqual(result.referring.fragment, "")
        self.assertEqual(result.referring.fragment_lc, "")
        self.assertEqual(result.referring.path, "")
        self.assertEqual(result.referring.path_lc, "")
        self.assertEqual(result.referring.query, "")
        self.assertEqual(result.referring.query_lc, "")
        self.assertEqual(result.referring.subdomain, "")
        self.assertEqual(result.referring.subdomain_lc, "")
        self.assertEqual(result.referring.top_level_domain, "")
        self.assertEqual(result.referring.top_level_domain_lc, "")
        self.assertEqual(result.referring.url, "")
        self.assertEqual(result.referring.url_lc, "")
        # user
        self.assertEqual(result.user.browser_type, "unknown")
        self.assertEqual(result.user.platform, "Unknown")
        self.assertEqual(result.user.locale, "en")
        self.assertEqual(result.user.browser_version, -1)

    def validate_object_values(self, obj):
        """Verify truthiness for all values in the obj"""
        for val in obj.__dict__.values():
            self.assertTrue(val)

    def test_create_decisioning_context(self):
        geo = Geo(country_code="US",
                  state_code="CA",
                  city="San Francisco",
                  latitude=38.8,
                  longitude=-77.0
                  )
        address = Address(url=TEST_URL, referring_url=TEST_URL)
        request_context = Context(channel=ChannelType.WEB, user_agent=FIREFOX_USER_AGENT, address=address, geo=geo)
        request = DeliveryRequest(context=request_context)

        result = create_decisioning_context(request)

        self.assertTrue(isinstance(result, DecisioningContext))
        self.assertIsNotNone(result.current_time)
        self.assertIsNotNone(result.current_timestamp)
        self.assertIsNotNone(result.current_day)
        self.validate_object_values(result.geo)
        self.validate_object_values(result.user)
        self.validate_object_values(result.page)
        self.validate_object_values(result.referring)
