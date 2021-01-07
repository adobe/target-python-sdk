# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Test cases for __init__.py"""
import unittest

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from target_python_sdk import TargetClient


class TestTargetClient(unittest.TestCase):

    def test_create_missing_options(self):
        with self.assertRaises(Exception) as err:
            TargetClient.create()
        self.assertEqual(str(err.exception), 'Options map is required')

    def test_create_missing_client(self):
        options = {
            'organization_id': "orgId"
        }
        with self.assertRaises(Exception) as err:
            TargetClient.create(options)
        self.assertEqual(str(err.exception), 'Client is required')

    def test_create_missing_organization_id(self):
        options = {
            'client': "clientId"
        }
        with self.assertRaises(Exception) as err:
            TargetClient.create(options)
        self.assertEqual(str(err.exception), 'Organization Id is required')

    def test_create_invalid_decisioning_method(self):
        options = {
            'client': "clientId",
            'organization_id': "orgId",
            'decisioning_method': "bad decisions"
        }

        with self.assertRaises(Exception) as err:
            TargetClient.create(options)
            self.assertEqual(str(err.exception),
                             'Invalid Decisioning Method.  Must be set to one of: on-device,server-side,hybrid')

    def test_create_custom_fetch_api(self):
        mock_fetch_api = Mock()
        options = {
            'client': "clientId",
            'organization_id': "orgId",
            'fetch_api': mock_fetch_api
        }
        client = TargetClient.create(options)
        self.assertEqual(client.config['fetch_api'], mock_fetch_api)

    def test_create_return_client(self):
        options = {
            'client': "clientId",
            'organization_id': "orgId"
        }
        client = TargetClient.create(options)
        self.assertIsNotNone(client)
