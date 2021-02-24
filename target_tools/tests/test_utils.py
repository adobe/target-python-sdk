# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Test cases for utils.py"""
import unittest
from copy import deepcopy
from urllib3_mock import Responses
from delivery_api_client import ChannelType
from target_python_sdk import TargetClient
from target_python_sdk.tests.delivery_request_setup import create_delivery_request
from target_tools.utils import get_mbox_names
from target_tools.utils import add_mboxes_to_request

responses = Responses("requests.packages.urllib3")


class TestUtils(unittest.TestCase):

    def setUp(self):
        client_options = {
            "client": "someClientId",
            "organization_id": "someOrgId"
        }
        self.get_attributes_options = {
            "request": {
                "context": {"channel": ChannelType.WEB},
                "execute": {
                    "mboxes": [{"name": "one"}, {"name": "two"}]
                },
                "prefetch": {
                    "mboxes": [{"name": "three"}, {"name": "four"}]
                }
            }
        }
        self.client = TargetClient.create(client_options)

    def test_get_mbox_names(self):
        opts = deepcopy(self.get_attributes_options)
        opts["request"] = create_delivery_request(opts["request"])

        result = get_mbox_names(opts["request"])
        self.assertTrue(isinstance(result, set))
        self.assertEqual(len(result), 4)
        self.assertTrue("one" in result)
        self.assertTrue("two" in result)
        self.assertTrue("three" in result)
        self.assertTrue("four" in result)

    def test_add_mboxes_to_request_adds_prefetch(self):
        opts = deepcopy(self.get_attributes_options)
        prefetch = {
            "mboxes": []
        }
        opts["request"]["prefetch"] = prefetch
        opts["request"]["execute"] = None
        opts["request"] = create_delivery_request(opts["request"])

        mboxes_to_add = ["mbox-foo", "mbox-bar", "mbox-baz"]
        add_mboxes_to_request(
            mboxes_to_add,
            opts["request"],
            "prefetch"
        )

        self.assertEqual(len(opts["request"].prefetch.mboxes), 3)
        for index, mbox in enumerate(opts["request"].prefetch.mboxes):
            self.assertEqual(mbox.index, index + 1)
            self.assertEqual(mbox.name, mboxes_to_add[index])

    def test_add_mboxes_to_request_adds_execute(self):
        opts = deepcopy(self.get_attributes_options)
        execute = {
            "mboxes": []
        }
        opts["request"]["prefetch"] = None
        opts["request"]["execute"] = execute
        opts["request"] = create_delivery_request(opts["request"])

        mboxes_to_add = ["mbox-foo", "mbox-bar", "mbox-baz"]
        add_mboxes_to_request(
            mboxes_to_add,
            opts["request"],
            "execute"
        )

        self.assertEqual(len(opts["request"].execute.mboxes), 3)
        for index, mbox in enumerate(opts["request"].execute.mboxes):
            self.assertEqual(mbox.index, index + 1)
            self.assertEqual(mbox.name, mboxes_to_add[index])

    def test_add_mboxes_to_request_no_duplicates_preserves_existing(
            self):
        opts = deepcopy(self.get_attributes_options)

        prefetch = {
            "mboxes": [
                {
                    "name": "mbox-foo",
                    "index": 6
                },
                {
                    "name": "mbox-jab",
                    "index": 2
                }
            ]
        }
        opts["request"]["prefetch"] = prefetch
        opts["request"]["execute"] = None

        opts["request"] = create_delivery_request(opts["request"])

        mboxes_to_add = ["mbox-foo", "mbox-bar", "mbox-baz"]
        add_mboxes_to_request(
            mboxes_to_add,
            opts["request"],
            "prefetch"
        )

        self.assertEqual(len(opts["request"].prefetch.mboxes), 4)
        resulting_mboxes = opts["request"].prefetch.mboxes
        self.assertEqual(resulting_mboxes[0].index, 6)
        self.assertEqual(resulting_mboxes[0].name, "mbox-foo")
        self.assertEqual(resulting_mboxes[1].index, 2)
        self.assertEqual(resulting_mboxes[1].name, "mbox-jab")
        self.assertEqual(resulting_mboxes[2].index, 7)
        self.assertEqual(resulting_mboxes[2].name, "mbox-bar")
        self.assertEqual(resulting_mboxes[3].index, 8)
        self.assertEqual(resulting_mboxes[3].name, "mbox-baz")
