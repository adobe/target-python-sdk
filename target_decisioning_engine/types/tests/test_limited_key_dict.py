# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Tests cases for LimitedKeyDict"""
# pylint: disable=super-init-not-called
import unittest

from target_tools.types.limited_key_dict import LimitedKeyDict


class DictImpl(LimitedKeyDict):
    """Child class for testing out the LimitedKeyDict base class"""

    __attribute_map = {
        "a": "str",
        "b": "int",
        "c": "bool"
    }

    def __init__(self, kwargs=None):
        """kwargs should only consist of keys inside __attribute_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return DictImpl.__attribute_map.keys()


class TestLimitedKeyDict(unittest.TestCase):
    """TestLimitedKeyDict"""

    def test_invalid_instance(self):
        with self.assertRaises(NotImplementedError):
            LimitedKeyDict()

    def test_invalid_keys_on_creation(self):
        test_dict = DictImpl({"bad": "val", "a": "foo", "b": 2})
        self.assertEqual(test_dict, {"a": "foo", "b": 2})

    def test_set_invalid_key(self):
        test_dict = DictImpl()
        with self.assertRaises(KeyError):
            test_dict["bad"] = "oh no"

    def test_set_valid_key(self):
        test_dict = DictImpl({"a": "foo"})
        test_dict["b"] = 100
        test_dict["c"] = True

        self.assertEqual(test_dict.get("a"), "foo")
        self.assertEqual(test_dict.get("b"), 100)
        self.assertEqual(test_dict.get("c"), True)
