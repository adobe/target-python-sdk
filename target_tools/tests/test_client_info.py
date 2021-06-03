# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Unit tests for target_decisioning_engine.client_info module"""
import unittest

from target_tools.client_info import browser_from_user_agent
from target_tools.client_info import operating_system_from_user_agent
from target_tools.client_info import device_type_from_user_agent

IE11_WIN = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"

IE11_COMPAT_WIN = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/8.0; .NET4.0C; .NET4.0E)"

FIREFOX_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0"

SAFARI_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 \
(KHTML, like Gecko) Version/13.1.1 Safari/605.1.15"

SAFARI_MOBILE = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 \
(KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1"

CHROME_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"

EDGE_WIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.61"

ANDROID = "Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) \
AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"

IPOD = "Mozilla/5.0 (iPod touch; CPU iPhone OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 \
(KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.53"

IPAD = "Mozilla/5.0 (iPad; U; CPU OS 11_2 like Mac OS X; zh-CN; iPad5,3) AppleWebKit/534.46 \
(KHTML, like Gecko) UCBrowser/3.0.1.776 U3/ Mobile/10A403 Safari/7543.48.3"

UNKNOWN = "Unknown"
UNKNOWN_VERSION = -1


class TestClientInfo(unittest.TestCase):

    def validate_browser(self, result, browser, version):
        """Validates browser name and version"""
        self.assertEqual(result.get("name"), browser)
        self.assertEqual(result.get("version"), version)

    def test_browser_from_user_agent_no_agent(self):
        result = browser_from_user_agent()
        self.validate_browser(result, UNKNOWN, UNKNOWN_VERSION)

    def test_browser_from_user_agent_unknown_agent(self):
        result = browser_from_user_agent("bad secret agent")
        self.validate_browser(result, UNKNOWN, UNKNOWN_VERSION)

    def test_browser_from_user_agent_ie_11(self):
        result = browser_from_user_agent(IE11_WIN)
        self.validate_browser(result, "IE", 11)

    def test_browser_from_user_agent_ie_7(self):
        result = browser_from_user_agent(IE11_COMPAT_WIN)
        self.validate_browser(result, "IE", 11)

    def test_browser_from_user_agent_firefox_78(self):
        result = browser_from_user_agent(FIREFOX_MAC)
        self.validate_browser(result, "Firefox", 78)

    def test_browser_from_user_agent_safari_13(self):
        result = browser_from_user_agent(SAFARI_MAC)
        self.validate_browser(result, "Safari", 13)

    def test_browser_from_user_agent_mobile_safari_13(self):
        result = browser_from_user_agent(SAFARI_MOBILE)
        self.validate_browser(result, "Mobile Safari", 13)

    def test_browser_from_user_agent_chrome_83(self):
        result = browser_from_user_agent(CHROME_MAC)
        self.validate_browser(result, "Chrome", 83)

    def test_browser_from_user_agent_edge_83(self):
        result = browser_from_user_agent(EDGE_WIN)
        self.validate_browser(result, "Edge", 83)

    def test_operating_system_from_user_agent_chrome_mac(self):
        os_name = operating_system_from_user_agent(CHROME_MAC)
        self.assertEqual(os_name, "Mac OS X")

    def test_operating_system_from_user_agent_ie_11(self):
        os_name = operating_system_from_user_agent(IE11_WIN)
        self.assertEqual(os_name, "Windows")

    def test_operating_system_from_user_agent_ie_11_compat(self):
        os_name = operating_system_from_user_agent(IE11_COMPAT_WIN)
        self.assertEqual(os_name, "Windows")

    def test_operating_system_from_user_agent_safari_mobile(self):
        os_name = operating_system_from_user_agent(SAFARI_MOBILE)
        self.assertEqual(os_name, "iOS")

    def test_operating_system_from_user_agent_android(self):
        os_name = operating_system_from_user_agent(ANDROID)
        self.assertEqual(os_name, "Android")

    def test_operating_system_from_user_agent_ipod(self):
        os_name = operating_system_from_user_agent(IPOD)
        self.assertEqual(os_name, "iOS")

    def test_operating_system_from_user_agent_ipad(self):
        os_name = operating_system_from_user_agent(IPAD)
        self.assertEqual(os_name, "iOS")

    def test_device_type_from_user_agent_safari_mobile(self):
        device_type = device_type_from_user_agent(SAFARI_MOBILE)
        self.assertEqual(device_type, "iPhone")

    def test_device_type_from_user_agent_ie_11(self):
        device_type = device_type_from_user_agent(IE11_WIN)
        self.assertEqual(device_type, "Desktop")

    def test_device_type_from_user_agent_chrome(self):
        device_type = device_type_from_user_agent(CHROME_MAC)
        self.assertEqual(device_type, "Mac")

    def test_device_type_from_user_agent_firefox(self):
        device_type = device_type_from_user_agent(FIREFOX_MAC)
        self.assertEqual(device_type, "Mac")

    def test_device_type_from_user_agent_safari(self):
        device_type = device_type_from_user_agent(SAFARI_MAC)
        self.assertEqual(device_type, "Mac")

    def test_device_type_from_user_agent_edge(self):
        device_type = device_type_from_user_agent(EDGE_WIN)
        self.assertEqual(device_type, "Desktop")

    def test_device_type_from_user_agent_ipod(self):
        device_type = device_type_from_user_agent(IPOD)
        self.assertEqual(device_type, "iPod")

    def test_device_type_from_user_agent_ipad(self):
        device_type = device_type_from_user_agent(IPAD)
        self.assertEqual(device_type, "iPad")
