# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Validation helper functions for test cases"""
from delivery_api_client import DeliveryResponse
from delivery_api_client import DeliveryRequest
from delivery_api_client import ExecuteResponse
from delivery_api_client import View
from delivery_api_client import PrefetchResponse
from delivery_api_client import PageLoadResponse
from delivery_api_client import MboxResponse
from delivery_api_client import PrefetchMboxResponse


def validate_option(_self, option):
    """Simple Option validation"""
    _self.assertIsNotNone(option)
    _self.assertIsNotNone(option.type)
    _self.assertIsNotNone(option.content)


def validate_page_load(_self, page_load_resp):
    """Validate pageload"""
    _self.assertIsNotNone(page_load_resp)
    _self.assertTrue(isinstance(page_load_resp, PageLoadResponse))
    _self.assertIsNotNone(page_load_resp.options)
    for option in page_load_resp.options:
        validate_option(_self, option)


def validate_mboxes(_self, mboxes_resp, mboxes_req, is_prefetch=False):
    """Validate mboxes"""
    mbox_type = PrefetchMboxResponse if is_prefetch else MboxResponse
    _self.assertIsNotNone(mboxes_resp)
    _self.assertTrue(isinstance(mboxes_resp, list))
    _self.assertEqual(len(mboxes_resp), len(mboxes_req))
    for mbox in mboxes_resp:
        _self.assertTrue(isinstance(mbox, mbox_type))
        _self.assertIsNotNone(mbox.index)
        _self.assertIsNotNone(mbox.name)
        _self.assertIsNotNone(mbox.options)
        for option in mbox.options:
            validate_option(_self, option)


def validate_execute(_self, execute_resp, execute_req):
    """Validate execute"""
    _self.assertIsNotNone(execute_resp)
    _self.assertTrue(isinstance(execute_resp, ExecuteResponse))
    if execute_req.page_load:
        validate_page_load(_self, execute_resp.page_load)
    if execute_req.mboxes:
        validate_mboxes(_self, execute_resp.mboxes, execute_req.mboxes)


def validate_views(_self, views_resp, views_req):
    """Validate views"""
    _self.assertIsNotNone(views_resp)
    _self.assertTrue(isinstance(views_resp, list))
    _self.assertEqual(len(views_resp), len(views_req))
    for view in views_resp:
        _self.assertTrue(isinstance(view, View))
        _self.assertIsNotNone(view.name)
        _self.assertIsNotNone(view.options)
        for option in view.options:
            validate_option(_self, option)


def validate_prefetch(_self, prefetch_resp, prefetch_req):
    """Validate prefetch"""
    _self.assertIsNotNone(prefetch_resp)
    _self.assertTrue(isinstance(prefetch_resp, PrefetchResponse))
    if prefetch_req.page_load:
        validate_page_load(_self, prefetch_resp.page_load)
    if prefetch_req.mboxes:
        validate_mboxes(_self, prefetch_resp.mboxes, prefetch_req.mboxes, is_prefetch=True)
    if prefetch_req.views:
        validate_views(_self, prefetch_resp.views, prefetch_req.views)


def validate_visitor_id(_self, visitor_id_resp, visitor_id_req):
    """Simple VisitorId validation"""
    if visitor_id_req.tnt_id:
        _self.assertIsNotNone(visitor_id_resp.tnt_id)
    if visitor_id_req.customer_ids:
        _self.assertIsNotNone(visitor_id_resp.customer_ids)
    if visitor_id_req.third_party_id:
        _self.assertIsNotNone(visitor_id_resp.third_party_id)
    if visitor_id_req.marketing_cloud_visitor_id:
        _self.assertIsNotNone(visitor_id_resp.marketing_cloud_visitor_id)


def validate_delivery_response(_self, get_offers_resp, get_offers_req):
    """Simple DeliveryResponse validation, based on DeliveryRequest
    :param _self (unittest.TestCase) required
    :param get_offers_resp (DeliveryResponse) result from get_offers call, required
    :param get_offers_req (DeliveryRequest) input options for get_offers, required
    """
    _self.assertIsNotNone(get_offers_resp.client)
    _self.assertIsNotNone(get_offers_resp.edge_host)
    _self.assertIsNotNone(get_offers_resp.id)
    validate_visitor_id(_self, get_offers_resp.id, get_offers_req.id)
    _self.assertIsNotNone(get_offers_resp.request_id)
    _self.assertEqual(get_offers_resp.status, 200)
    if get_offers_req.execute:
        validate_execute(_self, get_offers_resp.execute, get_offers_req.execute)
    if get_offers_req.prefetch:
        validate_prefetch(_self, get_offers_resp.prefetch, get_offers_req.prefetch)


def validate_response(_self, result):
    """Static get_offers validation
    :param _self (unittest.TestCase) required
    :param result (dict) Wrapper around DeliveryResponse payload
    """
    get_offers_resp = result.get('response')
    get_offers_req = result.get('request')
    _self.assertIsNotNone(get_offers_resp)
    _self.assertIsNotNone(get_offers_req)
    _self.assertTrue(isinstance(get_offers_resp, DeliveryResponse))
    _self.assertTrue(isinstance(get_offers_req, DeliveryRequest))
    validate_delivery_response(_self, get_offers_resp, get_offers_req)
