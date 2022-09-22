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

        self.assertTrue(isinstance(result.get("user"), UserContext))
        self.assertEqual(result.get("user").get("browserType"), "firefox")
        self.assertEqual(result.get("user").get("platform"), "Windows")
        self.assertEqual(result.get("user").get("locale"), "en")
        self.assertEqual(result.get("user").get("browserVersion"), 47)

    def test_create_page_context_url_empty_string(self):
        address = Address(url=EMPTY_STRING)
        result = create_page_context(address)

        self.assertTrue(isinstance(result, PageContext))
        for key in result.values():
            self.assertEqual(key, EMPTY_STRING)

    def test_create_page_context_non_empty_url(self):
        address = Address(url=TEST_URL)
        result = create_page_context(address)

        self.assertTrue(isinstance(result, PageContext))
        self.assertEqual(result.get("domain"), "geocities")
        self.assertEqual(result.get("domain_lc"), "geocities")
        self.assertEqual(result.get("fragment"), "Bottom")
        self.assertEqual(result.get("fragment_lc"), "bottom")
        self.assertEqual(result.get("path"), "/Posts")
        self.assertEqual(result.get("path_lc"), "/posts")
        self.assertEqual(result.get("query"), "Page=1")
        self.assertEqual(result.get("query_lc"), "page=1")
        self.assertEqual(result.get("subdomain"), "blog.myfavesite")
        self.assertEqual(result.get("subdomain_lc"), "blog.myfavesite")
        self.assertEqual(result.get("topLevelDomain"), "com")
        self.assertEqual(result.get("topLevelDomain_lc"), "com")
        self.assertEqual(result.get("url"), "http://Blog.Myfavesite.GeoCities.com/Posts?Page=1#Bottom")
        self.assertEqual(result.get("url_lc"), "http://blog.myfavesite.geocities.com/posts?page=1#bottom")

    def test_create_page_context_applookout(self):
        address = Address(url="https://stage.applookout.net/")
        result = create_page_context(address)

        self.assertTrue(isinstance(result, PageContext))
        self.assertEqual(result.get("domain"), "applookout")
        self.assertEqual(result.get("domain_lc"), "applookout")
        self.assertEqual(result.get("fragment"), "")
        self.assertEqual(result.get("fragment_lc"), "")
        self.assertEqual(result.get("path"), "/")
        self.assertEqual(result.get("path_lc"), "/")
        self.assertEqual(result.get("query"), "")
        self.assertEqual(result.get("query_lc"), "")
        self.assertEqual(result.get("subdomain"), "stage")
        self.assertEqual(result.get("subdomain_lc"), "stage")
        self.assertEqual(result.get("topLevelDomain"), "net")
        self.assertEqual(result.get("topLevelDomain_lc"), "net")
        self.assertEqual(result.get("url"), "https://stage.applookout.net/")
        self.assertEqual(result.get("url_lc"), "https://stage.applookout.net/")

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
        self.assertEqual(result.get("domain"), "geocities")
        self.assertEqual(result.get("domain_lc"), "geocities")
        self.assertEqual(result.get("fragment"), "Bottom")
        self.assertEqual(result.get("fragment_lc"), "bottom")
        self.assertEqual(result.get("path"), "/Posts")
        self.assertEqual(result.get("path_lc"), "/posts")
        self.assertEqual(result.get("query"), "Page=1")
        self.assertEqual(result.get("query_lc"), "page=1")
        self.assertEqual(result.get("subdomain"), "blog.myfavesite")
        self.assertEqual(result.get("subdomain_lc"), "blog.myfavesite")
        self.assertEqual(result.get("topLevelDomain"), "com")
        self.assertEqual(result.get("topLevelDomain_lc"), "com")
        self.assertEqual(result.get("url"), "http://Blog.Myfavesite.GeoCities.com/Posts?Page=1#Bottom")
        self.assertEqual(result.get("url_lc"), "http://blog.myfavesite.geocities.com/posts?page=1#bottom")

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

    def test_create_mbox_context_dot_notation(self):
        params = {
            "favorite_actor" : "dennehy",
            "dot.notation.is_now_in" : True,
            "dot.notation.threshold" : 1000,
            "dot.notation.declaration" : "All YOUR BASE ARE BELONG TO US",
            ".dont_support_this" : True,
            "nor_this." : True,
            "even..this..is..bad": True
        }
        mbox = MboxRequest(parameters=params)
        result = create_mbox_context(mbox)
        self.assertEqual(result, {
            ".dont_support_this": True,
            "dot": {"notation": {"is_now_in": True,
                                "threshold": 1000,
                                "declaration": "All YOUR BASE ARE BELONG TO US",
                                "declaration_lc": "all your base are belong to us"}},
            "even..this..is..bad": True,
            "favorite_actor": "dennehy",
            "favorite_actor_lc": "dennehy",
            "nor_this.": True})

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
        self.assertEqual(result.get("country"), "US")
        self.assertEqual(result.get("region"), "CA")
        self.assertEqual(result.get("city"), "San Francisco")
        self.assertEqual(result.get("latitude"), 38.8)
        self.assertEqual(result.get("longitude"), -77.0)

    def test_create_timing_context(self):
        request_context = Context(ChannelType.WEB)
        request = DeliveryRequest(context=request_context)

        result = create_decisioning_context(request)

        self.assertTrue(result.get("current_day") > 0)
        self.assertTrue(result.get("current_day") < 8)
        self.assertEqual(len(result.get("current_time")), 4)
        self.assertTrue(result.get("current_timestamp") > 0)

    def test_create_decisioning_context_generate_blank_context(self):
        request_context = Context(ChannelType.WEB)
        request = DeliveryRequest(context=request_context)

        result = create_decisioning_context(request)

        self.assertTrue(isinstance(result, DecisioningContext))
        # timing
        self.assertIsNotNone(result.get("current_time"))
        self.assertIsNotNone(result.get("current_timestamp"))
        self.assertIsNotNone(result.get("current_day"))
        # geo
        self.assertIsNone(result.get("geo").get("latitude"))
        self.assertIsNone(result.get("geo").get("longitude"))
        self.assertIsNone(result.get("geo").get("country"))
        self.assertIsNone(result.get("geo").get("region"))
        self.assertIsNone(result.get("geo").get("city"))
        # page
        self.assertEqual(result.get("page").get("domain"), "")
        self.assertEqual(result.get("page").get("domain_lc"), "")
        self.assertEqual(result.get("page").get("fragment"), "")
        self.assertEqual(result.get("page").get("fragment_lc"), "")
        self.assertEqual(result.get("page").get("path"), "")
        self.assertEqual(result.get("page").get("path_lc"), "")
        self.assertEqual(result.get("page").get("query"), "")
        self.assertEqual(result.get("page").get("query_lc"), "")
        self.assertEqual(result.get("page").get("subdomain"), "")
        self.assertEqual(result.get("page").get("subdomain_lc"), "")
        self.assertEqual(result.get("page").get("topLevelDomain"), "")
        self.assertEqual(result.get("page").get("topLevelDomain_lc"), "")
        self.assertEqual(result.get("page").get("url"), "")
        self.assertEqual(result.get("page").get("url_lc"), "")
        # referring
        self.assertEqual(result.get("referring").get("domain"), "")
        self.assertEqual(result.get("referring").get("domain_lc"), "")
        self.assertEqual(result.get("referring").get("fragment"), "")
        self.assertEqual(result.get("referring").get("fragment_lc"), "")
        self.assertEqual(result.get("referring").get("path"), "")
        self.assertEqual(result.get("referring").get("path_lc"), "")
        self.assertEqual(result.get("referring").get("query"), "")
        self.assertEqual(result.get("referring").get("query_lc"), "")
        self.assertEqual(result.get("referring").get("subdomain"), "")
        self.assertEqual(result.get("referring").get("subdomain_lc"), "")
        self.assertEqual(result.get("referring").get("topLevelDomain"), "")
        self.assertEqual(result.get("referring").get("topLevelDomain_lc"), "")
        self.assertEqual(result.get("referring").get("url"), "")
        self.assertEqual(result.get("referring").get("url_lc"), "")
        # user
        self.assertEqual(result.get("user").get("browserType"), "unknown")
        self.assertEqual(result.get("user").get("platform"), "Unknown")
        self.assertEqual(result.get("user").get("locale"), "en")
        self.assertEqual(result.get("user").get("browserVersion"), -1)

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
        self.assertIsNotNone(result.get("current_time"))
        self.assertIsNotNone(result.get("current_timestamp"))
        self.assertIsNotNone(result.get("current_day"))
        self.validate_object_values(result.get("geo"))
        self.validate_object_values(result.get("user"))
        self.validate_object_values(result.get("page"))
        self.validate_object_values(result.get("referring"))
