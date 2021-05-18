# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for utils.py"""
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
import unittest
import datetime
from copy import deepcopy
from urllib3_mock import Responses
from delivery_api_client import ChannelType
from target_python_sdk import TargetClient
from target_tools.tests.delivery_request_setup import create_delivery_request
from target_tools.utils import get_mbox_names
from target_tools.utils import memoize
from target_tools.utils import add_mboxes_to_request
from target_tools.utils import get_epoch_time
from target_tools.utils import is_empty
from target_tools.utils import get_epoch_time_milliseconds


MOCK_DATE = datetime.datetime(2021, 3, 22, 14, 53, 0, 30534)

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

    def test_memoize_default_args_resolver(self):
        mock_fn = Mock(return_value=100)
        test_fn = memoize(mock_fn)

        result = test_fn(1, x="memo", y=999)
        self.assertEqual(result, 100)
        result = test_fn(1, x="memo", y=999)
        self.assertEqual(result, 100)
        result = test_fn(1, x="memo", y=999)
        self.assertEqual(result, 100)
        self.assertEqual(mock_fn.call_count, 1)
        self.assertEqual(mock_fn.call_args[0][0], 1)
        self.assertEqual(mock_fn.call_args[1].get("x"), "memo")
        self.assertEqual(mock_fn.call_args[1].get("y"), 999)

        test_fn(1, x="no match", y=111)
        test_fn(1, x="memo")
        test_fn(1)
        test_fn()
        self.assertEqual(mock_fn.call_count, 5)

    def test_memoize_custom_args_resolver(self):
        def resolver(args, kwargs):
            key = ""
            for _arg in args:
                key += str(_arg)
            for _key, _val in list(kwargs.items()):
                key += "{}={}".format(_key, _val)
            return key

        mock_fn = Mock(return_value=100)
        test_fn = memoize(mock_fn, args_resolver=resolver)

        result = test_fn(1, x="memo", y=999)
        self.assertEqual(result, 100)
        result = test_fn(1, x="memo", y=999)
        self.assertEqual(result, 100)
        result = test_fn(1, x="memo", y=999)
        self.assertEqual(result, 100)
        self.assertEqual(mock_fn.call_count, 1)
        self.assertEqual(mock_fn.call_args[0][0], 1)
        self.assertEqual(mock_fn.call_args[1].get("x"), "memo")
        self.assertEqual(mock_fn.call_args[1].get("y"), 999)

        test_fn(1, x="no match", y=111)
        test_fn(1, x="memo")
        test_fn(1)
        test_fn()
        self.assertEqual(mock_fn.call_count, 5)

    def test_get_epoch_time_now(self):
        with patch("target_tools.utils.datetime.datetime", Mock(wraps=datetime.datetime)) as mock_datetime:
            mock_datetime.utcnow.return_value = MOCK_DATE
            result = get_epoch_time()
            self.assertEqual(result, 1616424781)
            self.assertEqual(mock_datetime.utcnow.call_count, 1)

    def test_get_epoch_time_passed_datetime(self):
        with patch("target_tools.utils.datetime.datetime", Mock(wraps=datetime.datetime)) as mock_datetime:
            result = get_epoch_time(MOCK_DATE)
            self.assertEqual(result, 1616424781)
            self.assertEqual(mock_datetime.utcnow.call_count, 0)

    def test_get_epoch_time_milliseconds_now(self):
        with patch("target_tools.utils.datetime.datetime", Mock(wraps=datetime.datetime)) as mock_datetime:
            mock_datetime.utcnow.return_value = MOCK_DATE
            result = get_epoch_time_milliseconds()
            self.assertEqual(result, 1616424781000)
            self.assertEqual(mock_datetime.utcnow.call_count, 1)

    def test_get_epoch_time_milliseconds_passed_datetime(self):
        with patch("target_tools.utils.datetime.datetime", Mock(wraps=datetime.datetime)) as mock_datetime:
            result = get_epoch_time_milliseconds(MOCK_DATE)
            self.assertEqual(result, 1616424781000)
            self.assertEqual(mock_datetime.utcnow.call_count, 0)

    def test_is_empty_list(self):
        self.assertTrue(is_empty(None))
        self.assertTrue(is_empty(""))
        self.assertTrue(is_empty([]))
        self.assertTrue(is_empty({}))
        self.assertTrue(is_empty(set()))
        self.assertTrue(is_empty(tuple()))

        self.assertFalse(is_empty("not empty"))
        self.assertFalse(is_empty([1]))
        self.assertFalse(is_empty({"a": "b"}))
        self.assertFalse(is_empty(set([1, 2, 3])))
        self.assertFalse(is_empty(tuple(["x", "y"])))
