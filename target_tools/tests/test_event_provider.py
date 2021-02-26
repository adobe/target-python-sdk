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
from target_tools.event_provider import EventProvider

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class TestEventsProvider(unittest.TestCase):

    def test_emit_without_payload(self):
        called = {"was_called": False}

        def aloha(event):
            called["was_called"] = True
            self.assertEqual(event, {
                'type': "aloha"
            })

        event_provider = EventProvider({
            "aloha": aloha
        })
        event_provider.emit("aloha")
        self.assertTrue(called["was_called"])

    def test_emit_with_payload(self):
        called = {"was_called": False}

        def aloha(event):
            called["was_called"] = True
            self.assertEqual(event, {
                'type': "aloha",
                'data': {
                    'value': "hello"
                },
                'code': 11
            })

        event_provider = EventProvider({
            "aloha": aloha
        })
        event_provider.emit("aloha", {
            'data': {
                'value': "hello"
            },
            'code': 11
        })
        self.assertTrue(called["was_called"])

    def test_subscribe(self):
        called = {"was_called": False}

        def aloha(event):
            called["was_called"] = True
            self.assertEqual(event, {
                'type': "aloha"
            })

        event_provider = EventProvider()
        event_provider.subscribe("aloha", aloha)
        event_provider.emit("aloha")

        self.assertEqual(event_provider.subscription_count, 1)
        self.assertTrue(called["was_called"])

    def test_unsubscribe(self):
        aloha = MagicMock()

        event_provider = EventProvider()
        subscription_id = event_provider.subscribe("aloha", aloha)
        self.assertEqual(event_provider.subscription_count, 1)

        event_provider.emit("aloha")
        event_provider.unsubscribe(subscription_id)

        event_provider.emit("aloha")
        event_provider.emit("aloha")
        event_provider.emit("aloha")

        self.assertEqual(aloha.call_count, 1)
        self.assertEqual(event_provider.subscription_count, 0)
