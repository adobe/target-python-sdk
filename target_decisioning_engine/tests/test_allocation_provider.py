# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for target_decisioning_enging.allocation_provider module"""
import unittest

from delivery_api_client import VisitorId
from delivery_api_client import CustomerId
from delivery_api_client import AuthenticatedState
from target_decisioning_engine.allocation_provider import compute_allocation
from target_decisioning_engine.allocation_provider import get_or_create_visitor_id
from target_decisioning_engine.allocation_provider import valid_tnt_id

CLIENT_ID = "someClientId"
ACTIVITY_ID = "123456"
SALT = "salty"


class TestAllocationProvider(unittest.TestCase):

    def test_compute_allocation_visitor_id_str(self):
        visitor_id = "ecid123"
        allocation = compute_allocation(CLIENT_ID, ACTIVITY_ID, visitor_id, SALT)
        self.assertEqual(allocation, 29.06)

    def test_compute_allocation_ecid(self):
        visitor_id = VisitorId(marketing_cloud_visitor_id="ecid123")
        allocation = compute_allocation(CLIENT_ID, ACTIVITY_ID, visitor_id, SALT)
        self.assertEqual(allocation, 29.06)

    def test_compute_allocation_tnt_id(self):
        visitor_id = VisitorId(tnt_id="tntId123")
        allocation = compute_allocation(CLIENT_ID, ACTIVITY_ID, visitor_id, SALT)
        self.assertEqual(allocation, 21.94)

    def test_compute_allocation_tnt_id_with_location_hint(self):
        visitor_id = VisitorId(tnt_id="tntId123.28_0")
        allocation = compute_allocation(CLIENT_ID, ACTIVITY_ID, visitor_id, SALT)
        self.assertEqual(allocation, 21.94)

    def test_compute_allocation_third_party_id(self):
        visitor_id = VisitorId(third_party_id="thirtPartyId123")
        allocation = compute_allocation(CLIENT_ID, ACTIVITY_ID, visitor_id, SALT)
        self.assertEqual(allocation, 73.15)

    def test_compute_allocation_generate_visitor_id(self):
        visitor_id = None
        allocation = compute_allocation(CLIENT_ID, ACTIVITY_ID, visitor_id, SALT)
        self.assertTrue(isinstance(allocation, float))
        self.assertTrue(allocation >= 0)
        self.assertTrue(allocation < 100)

        visitor_id = VisitorId()
        allocation = compute_allocation(CLIENT_ID, ACTIVITY_ID, visitor_id, SALT)
        self.assertTrue(isinstance(allocation, float))
        self.assertTrue(allocation >= 0)
        self.assertTrue(allocation < 100)

    def test_get_or_create_visitor_id_uses_ecid(self):
        customer_id = CustomerId(id="custId123", integration_code="A", authenticated_state=AuthenticatedState.UNKNOWN)
        visitor_id = VisitorId(tnt_id="tnt123",
                               marketing_cloud_visitor_id="mcid123",
                               customer_ids=[customer_id],
                               third_party_id="thirtPartyId123")
        result = get_or_create_visitor_id(visitor_id)
        self.assertEqual(result, "mcid123")

    def test_get_or_create_visitor_id_uses_tnt_id(self):
        customer_id = CustomerId(id="custId123", integration_code="A", authenticated_state=AuthenticatedState.UNKNOWN)
        visitor_id = VisitorId(tnt_id="tnt123",
                               customer_ids=[customer_id],
                               third_party_id="thirtPartyId123")
        result = get_or_create_visitor_id(visitor_id)
        self.assertEqual(result, "tnt123")

    def test_get_or_create_visitor_id_uses_third_party_id(self):
        customer_id = CustomerId(id="custId123", integration_code="A", authenticated_state=AuthenticatedState.UNKNOWN)
        visitor_id = VisitorId(customer_ids=[customer_id],
                               third_party_id="thirtPartyId123")
        result = get_or_create_visitor_id(visitor_id)
        self.assertEqual(result, "thirtPartyId123")

    def test_get_or_create_visitor_id_never_uses_customer_id(self):
        customer_ids = [
            CustomerId(id="custId123unknown", integration_code="A", authenticated_state=AuthenticatedState.UNKNOWN),
            CustomerId(id="custId123loggedout", integration_code="A",
                       authenticated_state=AuthenticatedState.LOGGED_OUT),
            CustomerId(id="custId123authenticated", integration_code="A",
                       authenticated_state=AuthenticatedState.AUTHENTICATED)
        ]
        visitor_id = VisitorId(customer_ids=customer_ids)
        result = get_or_create_visitor_id(visitor_id)
        self.assertTrue(isinstance(result, str))
        self.assertGreater(len(result), 0)
        self.assertIsNot(result, "custId123unknown")
        self.assertIsNot(result, "custId123loggedout")
        self.assertIsNot(result, "custId123authenticated")

    def test_get_or_create_visitor_id_generate_id(self):
        result = get_or_create_visitor_id("")
        self.assertTrue(isinstance(result, str))
        self.assertGreater(len(result), 0)

    def test_valid_tnt_id_strips_off_cluster(self):
        result = valid_tnt_id("338e3c1e51f7416a8e1ccba4f81acea0.28_0")
        self.assertEqual(result, "338e3c1e51f7416a8e1ccba4f81acea0")

    def test_valid_tnt_id_no_cluster(self):
        result = valid_tnt_id("338e3c1e51f7416a8e1ccba4f81acea0")
        self.assertEqual(result, "338e3c1e51f7416a8e1ccba4f81acea0")

    def test_valid_tnt_id_invalid(self):
        result = valid_tnt_id("")
        self.assertIsNone(result)

        result = valid_tnt_id(None)
        self.assertIsNone(result)

        result = valid_tnt_id()
        self.assertIsNone(result)

        result = valid_tnt_id(100)
        self.assertIsNone(result)
