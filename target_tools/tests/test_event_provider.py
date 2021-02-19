# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Test cases for events_provider.py"""

import unittest
from target_tools.attributes_provider import EventProvider

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

class TestEventsProvider(unittest.TestCase):

    def test_subscribes_to_an_event(self):
        print("")

    def test_subscribes_to_an_event_with_payload(self):
        print("")

    def test_supports_ad_hoc_subscriptions(self):
        print("")

    def test_supports_ad_hoc_unsubscribe(self):
        mock = MagicMock()
        aloha = mock

        event_provider = EventProvider()
        subscription_id = event_provider.subscribe("aloha", aloha)

        event_provider.emit("aloha")
        event_provider.unsubscribe(subscription_id)

        event_provider.emit("aloha")
        event_provider.emit("aloha")
        event_provider.emit("aloha")

        self.assertEqual(aloha.call_args_list, 1)