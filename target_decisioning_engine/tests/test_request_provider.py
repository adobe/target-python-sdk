# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for target_decisioning_engine.request_provider module"""
import unittest
from delivery_api_client import VisitorId, CustomerId, AuthenticatedState
from target_decisioning_engine.request_provider import valid_visitor_id

LOCATION_HINT = "08"


class TestRequestProvider(unittest.TestCase):

    def test_valid_visitor_id_existing_tnt_id(self):
        customer_ids = [CustomerId(id="custId123",
                                   integration_code="A",
                                   authenticated_state=AuthenticatedState.AUTHENTICATED)]
        visitor_id = VisitorId(tnt_id="tnt123",
                               third_party_id="thirdParty123",
                               marketing_cloud_visitor_id="mcid123",
                               customer_ids=customer_ids)
        result = valid_visitor_id(visitor_id, LOCATION_HINT)
        self.assertEqual(visitor_id, result)

    def test_valid_visitor_id_existing_third_party(self):
        visitor_id = VisitorId(third_party_id="thirdParty123")
        result = valid_visitor_id(visitor_id, LOCATION_HINT)
        self.assertEqual(visitor_id, result)

    def test_valid_visitor_id_existing_customer_id(self):
        customer_ids = [CustomerId(id="custId123",
                                   integration_code="A",
                                   authenticated_state=AuthenticatedState.AUTHENTICATED)]
        visitor_id = VisitorId(customer_ids=customer_ids)
        result = valid_visitor_id(visitor_id, LOCATION_HINT)
        self.assertEqual(visitor_id, result)

    def test_valid_visitor_id_existing_ecid(self):
        visitor_id = VisitorId(marketing_cloud_visitor_id="mcid123")
        result = valid_visitor_id(visitor_id, LOCATION_HINT)
        self.assertEqual(visitor_id, result)

    def test_valid_visitor_id_generate_tnt_id(self):
        visitor_id = VisitorId()
        result = valid_visitor_id(visitor_id, LOCATION_HINT)
        self.assertIsNotNone(result.tnt_id)

    def test_valid_visitor_id_invalid_customer_id(self):
        customer_ids = [CustomerId(id="custIdUnknown",
                                   integration_code="A",
                                   authenticated_state=AuthenticatedState.UNKNOWN),
                        CustomerId(id="custIdLoggedOut",
                                   integration_code="A",
                                   authenticated_state=AuthenticatedState.LOGGED_OUT)]
        visitor_id = VisitorId(customer_ids=customer_ids)
        result = valid_visitor_id(visitor_id, LOCATION_HINT)
        self.assertIsNotNone(result.tnt_id)
