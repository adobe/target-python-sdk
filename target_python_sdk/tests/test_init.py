# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Test cases for __init__.py"""
import json
import multiprocessing
import unittest
from copy import deepcopy

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import six
from urllib3_mock import Responses
import delivery_api_client
from delivery_api_client import ScreenOrientationType
from delivery_api_client import ApiClient
from delivery_api_client import ChannelType
from target_python_sdk import TargetClient
from target_python_sdk.tests.delivery_api_mock import setup_mock
from target_python_sdk.tests.validation import validate_response
from target_python_sdk.tests.delivery_request_setup import create_delivery_request
from target_python_sdk.tests.helpers import get_client_options
from target_python_sdk.tests.helpers import spy_decorator

responses = Responses('requests.packages.urllib3')


class TestTargetClient(unittest.TestCase):

    def setUp(self):
        client_options = get_client_options()
        self.get_offers_options = {
            'request': {
                'id': {
                    'tnt_id': '123'
                },
                'execute': {
                    'mboxes': [{
                        'name': 'cart',
                        'index': 1
                    }]
                },
                'prefetch': {
                    'mboxes': [{
                        'name': 'homepage',
                        'index': 1
                    }]
                },
                'context': {
                    'channel': ChannelType.WEB,
                    'application': {
                        'id': '123',
                        'name': 'unit testing python'
                    },
                    'screen': {
                        'width': 512,
                        'height': 512,
                        'color_depth': 100,
                        'orientation': ScreenOrientationType.PORTRAIT
                    },
                    'window': {
                        'width': 512,
                        'height': 512
                    },
                    'browser': {
                        'host': 'targetpythonsdk'
                    },
                    'address': {
                        'url': 'http://www.targetpythonsdk.com'
                    },
                    'geo': {
                        'latitude': 38.8,
                        'longitude': -77.0
                    }
                },
                'property': {
                    'token': '08b62abd-c3e7-dfb2-da93-96b3aa724d81'
                },
                'experience_cloud': {
                    'analytics': {
                        'supplemental_data_id': '234234987325982342342349873259823',
                        'tracking_server': 'ags041.sc.omtrdc.net',
                        'logging': 'server_side'
                    },
                    'audience_manager': {
                        'location_hint': 9,
                        'blob': '32fdghkjh34kj5h43'
                    }
                }
            }
        }
        self.client = TargetClient.create(client_options)

    def test_create_missing_options(self):
        with self.assertRaises(Exception) as err:
            TargetClient.create()
        self.assertEqual(str(err.exception), 'Options are required')

    def test_create_missing_client(self):
        options = {
            'organization_id': 'orgId'
        }
        with self.assertRaises(Exception) as err:
            TargetClient.create(options)
        self.assertEqual(str(err.exception), 'Client is required')

    def test_create_missing_organization_id(self):
        options = {
            'client': 'clientId'
        }
        with self.assertRaises(Exception) as err:
            TargetClient.create(options)
        self.assertEqual(str(err.exception), 'Organization Id is required')

    def test_create_invalid_decisioning_method(self):
        options = {
            'client': 'clientId',
            'organization_id': 'orgId',
            'decisioning_method': 'bad decisions'
        }
        with self.assertRaises(Exception) as err:
            TargetClient.create(options)
        self.assertEqual(str(err.exception),
                         'Invalid Decisioning Method.  Must be set to one of: hybrid,on-device,server-side')

    def test_create_return_client(self):
        options = {
            'client': 'clientId',
            'organization_id': 'orgId'
        }
        client = TargetClient.create(options)
        self.assertIsNotNone(client)

    def test_get_offers_no_options(self):
        with self.assertRaises(Exception) as err:
            self.client.get_offers({})
        self.assertEqual(str(err.exception), 'Options are required')

    def test_get_offers_no_request(self):
        opts = {'request': {}}
        with self.assertRaises(Exception) as err:
            self.client.get_offers(opts)
        self.assertEqual(str(err.exception), 'Request object of type DeliveryRequest is required')

    def test_get_offers_invalid_execute(self):
        request_opts = {
            'context': {
                'channel': 'web',
            },
            'execute': {
                'notmboxes': []
            }
        }

        opts = {
            'request': create_delivery_request(request_opts)
        }

        with self.assertRaises(Exception) as err:
            self.client.get_offers(opts)
        self.assertEqual(str(err.exception), 'Either pageLoad or mboxes is required in execute')

    def test_get_offers_invalid_prefetch(self):
        request_opts = {
            'context': {
                'channel': 'web',
            },
            'execute': {
                'mboxes': [{}]
            },
            'prefetch': {
                'notmboxes': []
            }
        }
        opts = {
            'request': create_delivery_request(request_opts)
        }
        with self.assertRaises(Exception) as err:
            self.client.get_offers(opts)
        self.assertEqual(str(err.exception), 'Either views, pageLoad or mboxes is required in prefetch')

    def test_get_offers_invalid_callback(self):
        request_opts = {
            'execute': {
                'mboxes': [{}]
            },
            'prefetch': {
                'mboxes': [{}]
            }
        }
        opts = {
            'request': create_delivery_request(request_opts),
            'callback': 'Should be a fn'
        }
        with self.assertRaises(Exception) as err:
            self.client.get_offers(opts)
        self.assertEqual(str(err.exception), 'Callback must be a callable function')

    @responses.activate
    def test_get_offers_async(self):
        setup_mock('default', responses)

        shared = {'has_response': False}
        async_opts = deepcopy(self.get_offers_options)
        async_opts['request'] = create_delivery_request(async_opts['request'])

        def verify_callback(result):
            self.assertEqual(len(responses.calls), 1)
            validate_response(self, result)
            shared['has_response'] = True

        async_opts['callback'] = verify_callback
        thread = self.client.get_offers(async_opts)
        try:
            thread.get(timeout=5)  # Blocks current thread to keep test runner alive
        except multiprocessing.context.TimeoutError:
            self.fail("Test case timed out waiting for callback to be invoked")
        self.assertTrue(shared.get('has_response'))

    @unittest.skipIf(six.PY2, "Python 2 doesn't support err_callback for apply_async")
    @responses.activate
    def test_get_offers_async_error(self):
        setup_mock('invalid_request', responses, 400)

        shared = {'has_response': False}
        client_options = {
            'client': 'bad',
            'organization_id': 'bad'
        }
        client = TargetClient.create(client_options)

        def callback():
            self.fail("Error callback should have been invoked")

        def err_callback(error):
            self.assertEqual(error.status, 400)
            self.assertEqual(json.loads(error.body),
                             {"status": 400, "message": "Invalid request: Invalid imsOrg -  bad"})
            shared['has_response'] = True

        async_opts = deepcopy(self.get_offers_options)
        async_opts['request'] = create_delivery_request(async_opts['request'])
        async_opts['callback'] = callback
        async_opts['err_callback'] = err_callback
        thread = client.get_offers(async_opts)

        try:
            thread.get(timeout=5)  # Blocks current thread to keep test runner alive
        except multiprocessing.context.TimeoutError:
            self.fail("Test case timed out waiting for callback to be invoked")
        except delivery_api_client.exceptions.ApiException:
            pass  # thread.get re-throws exception, but we've already handled inside err_callback

        self.assertTrue(shared.get('has_response'))

    @responses.activate
    def test_get_offers_sync(self):
        setup_mock('default', responses)
        opts = deepcopy(self.get_offers_options)
        opts['request'] = create_delivery_request(opts['request'])
        result = self.client.get_offers(opts)
        self.assertEqual(len(responses.calls), 1)
        validate_response(self, result)

    @responses.activate
    def test_get_offers_sync_error(self):
        setup_mock('invalid_request', responses, 400)
        client_options = {
            'client': 'bad',
            'organization_id': 'bad'
        }
        client = TargetClient.create(client_options)

        get_offers_opts = deepcopy(self.get_offers_options)
        get_offers_opts['request'] = create_delivery_request(get_offers_opts['request'])

        with self.assertRaises(delivery_api_client.exceptions.ApiException) as err:
            client.get_offers(get_offers_opts)
        self.assertEqual(json.loads(err.exception.body),
                         {"status": 400, "message": "Invalid request: Invalid imsOrg -  bad"})

    @responses.activate
    def test_get_offers_target_cookie(self):
        setup_mock('default', responses)
        opts = deepcopy(self.get_offers_options)
        opts['request'] = create_delivery_request(opts['request'])
        opts['target_cookie'] = 'PC#1.5_9#9596233214|b#2#1296233214'

        result = self.client.get_offers(opts)

        self.assertEqual(len(responses.calls), 1)
        validate_response(self, result)
        self.assertIsNotNone(result.get('target_cookie'))
        self.assertIsNotNone(result.get('target_location_hint_cookie'))

    @responses.activate
    def test_get_offers_customer_ids(self):
        setup_mock('customer_ids', responses)
        opts = deepcopy(self.get_offers_options)
        customer_ids = [{
            'id': '999',
            'integration_code': 'foo',
            'authenticated_state': 'authenticated'
        }]
        opts['request']['id']['customer_ids'] = customer_ids
        opts['request'] = create_delivery_request(opts['request'])

        result = self.client.get_offers(opts)

        self.assertEqual(len(responses.calls), 1)
        validate_response(self, result)

    @responses.activate
    def test_get_offers_execute(self):
        setup_mock('execute', responses)
        opts = deepcopy(self.get_offers_options)
        execute = {
            'mboxes': [{
                'name': 'cart',
                'index': 1
            }],
            'page_load': {
                'product': {
                    'id': '123',
                    'category_id': '456'
                },
                'order': {
                    'id': '111',
                    'total': 100
                }
            }
        }
        opts['request']['prefetch'] = None
        opts['request']['execute'] = execute
        opts['request'] = create_delivery_request(opts['request'])

        result = self.client.get_offers(opts)

        self.assertEqual(len(responses.calls), 1)
        validate_response(self, result)

    @responses.activate
    def test_get_offers_prefetch(self):
        setup_mock('prefetch', responses)
        opts = deepcopy(self.get_offers_options)
        prefetch = {
            'mboxes': [{
                'name': 'cart',
                'index': 1
            }],
            'page_load': {
                'product': {
                    'id': '123',
                    'category_id': '456'
                },
                'order': {
                    'id': '111',
                    'total': 100
                }
            },
            'views': [{
                'product': {
                    'id': '123',
                    'category_id': '456'
                },
                'order': {
                    'id': '111',
                    'total': 100
                }
            }]
        }
        opts['request']['execute'] = None
        opts['request']['prefetch'] = prefetch
        opts['request'] = create_delivery_request(opts['request'])

        result = self.client.get_offers(opts)

        self.assertEqual(len(responses.calls), 1)
        validate_response(self, result)
        response_tokens = result.get('response_tokens')
        self.assertIsNotNone(response_tokens)
        self.assertEqual(len(response_tokens), 2)
        for response_token in response_tokens:
            self.assertIsNotNone(response_token.get('activity.id'))
            self.assertIsNotNone(response_token.get('experience.id'))

    @responses.activate
    def test_get_offers_with_trace(self):
        setup_mock('debug_trace', responses)
        opts = deepcopy(self.get_offers_options)
        opts['request']['trace'] = {
            'authorization_token': 'token',
            'usage': {
                'a': 'b',
                'c': 'd'
            }
        }
        opts['request'] = create_delivery_request(opts['request'])

        request_spy = spy_decorator(ApiClient.request)
        with patch.object(ApiClient, 'request', request_spy):
            result = self.client.get_offers(opts)

            # validate Delivery API request
            expected_req_trace = request_spy.mock.call_args[1]['body']['trace']
            self.assertTrue(isinstance(expected_req_trace, dict))
            self.assertEqual(expected_req_trace.get('authorizationToken'), 'token')
            self.assertEqual(expected_req_trace.get('usage'), {
                'a': 'b',
                'c': 'd'
            })

            # validate Delivery API response
            self.assertEqual(len(responses.calls), 1)
            validate_response(self, result)

            if not result.get('response').execute.mboxes:
                self.fail('Expected execute mboxes in DeliveryResponse')
            for mbox in result.get('response').execute.mboxes:
                self.assertIsNotNone(mbox.trace)

            if not result.get('response').prefetch.mboxes:
                self.fail('Expected prefetch mboxes in DeliveryResponse')
            for mbox in result.get('response').prefetch.mboxes:
                self.assertIsNotNone(mbox.trace)
