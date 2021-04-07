# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for target_python_sdk.utils module"""
import datetime

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
import unittest
from target_python_sdk.utils import get_epoch_time
from target_python_sdk.utils import is_empty
from target_python_sdk.utils import get_epoch_time_milliseconds


MOCK_DATE = datetime.datetime(2021, 3, 22, 14, 53, 0, 30534)


class TestUtils(unittest.TestCase):

    def test_get_epoch_time_now(self):
        with patch("target_python_sdk.utils.datetime.datetime", Mock(wraps=datetime.datetime)) as mock_datetime:
            mock_datetime.utcnow.return_value = MOCK_DATE
            result = get_epoch_time()
            self.assertEqual(result, 1616424781)
            self.assertEqual(mock_datetime.utcnow.call_count, 1)

    def test_get_epoch_time_passed_datetime(self):
        with patch("target_python_sdk.utils.datetime.datetime", Mock(wraps=datetime.datetime)) as mock_datetime:
            result = get_epoch_time(MOCK_DATE)
            self.assertEqual(result, 1616424781)
            self.assertEqual(mock_datetime.utcnow.call_count, 0)

    def test_get_epoch_time_milliseconds_now(self):
        with patch("target_python_sdk.utils.datetime.datetime", Mock(wraps=datetime.datetime)) as mock_datetime:
            mock_datetime.utcnow.return_value = MOCK_DATE
            result = get_epoch_time_milliseconds()
            self.assertEqual(result, 1616424781000)
            self.assertEqual(mock_datetime.utcnow.call_count, 1)

    def test_get_epoch_time_milliseconds_passed_datetime(self):
        with patch("target_python_sdk.utils.datetime.datetime", Mock(wraps=datetime.datetime)) as mock_datetime:
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
