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

from target_tools import utils


class TestUtils(unittest.TestCase):

    def test_get_mbox_names(self):
        result = utils.get_mbox_names({
            'context': {'channel': "web"},
            'execute': {
                'mboxes': [{'name': "one"}, {'name': "two"}]
            },
            'prefetch': {
                'mboxes': [{'name': "three"}, {'name': "four"}]
            }
        })
        self.assertTrue(isinstance(result, set))
        self.assertEqual(len(result), 4)
        self.assertTrue("one" in result)
        self.assertTrue("two" in result)
        self.assertTrue("three" in result)
        self.assertTrue("four" in result)

    def test_add_mboxes_to_request_adds_prefetch(self):
        self.assertDictContainsSubset(
            {
                'prefetch': {
                    'mboxes': [
                        {
                            'name': "mbox-foo",
                            'index': 1
                        },
                        {
                            'name': "mbox-bar",
                            'index': 2
                        },
                        {
                            'name': "mbox-baz",
                            'index': 3
                        }
                    ]
                }
            },
            utils.add_mboxes_to_request(
                ["mbox-foo", "mbox-bar", "mbox-baz"],
                {
                    'context': {'channel': "web"},
                    'prefetch': {
                        'mboxes': []
                    }
                },
                "prefetch"
            )
        )

    def test_add_mboxes_to_request_adds_execute(self):
        self.assertDictContainsSubset(
            {
                'execute': {
                    'mboxes': [
                        {
                            'name': "mbox-foo",
                            'index': 1
                        },
                        {
                            'name': "mbox-bar",
                            'index': 2
                        },
                        {
                            'name': "mbox-baz",
                            'index': 3
                        }
                    ]
                }
            },
            utils.add_mboxes_to_request(
                ["mbox-foo", "mbox-bar", "mbox-baz"],
                {
                    'context': {'channel': "web"},
                    'execute': {
                        'mboxes': []
                    }
                },
                "execute"
            )
        )

    def test_add_mboxes_to_request_adds_without_duplicates_preserves_existings(
            self):
        self.assertDictContainsSubset(
            {
                'prefetch': {
                    'mboxes': [
                        {
                            'name': "mbox-foo",
                            'index': 6
                        },
                        {
                            'name': "mbox-jab",
                            'index': 2
                        },
                        {
                            'name': "mbox-bar",
                            'index': 7
                        },
                        {
                            'name': "mbox-baz",
                            'index': 8
                        }
                    ]
                }
            },
            utils.add_mboxes_to_request(
                ["mbox-foo", "mbox-bar", "mbox-baz"],
                {
                    'context': {'channel': "web"},
                    'prefetch': {
                        'mboxes': [
                            {
                                'name': "mbox-foo",
                                'index': 6
                            },
                            {
                                'name': "mbox-jab",
                                'index': 2
                            }
                        ]
                    }
                },
                "prefetch"
            )
        )
