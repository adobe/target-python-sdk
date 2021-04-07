# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Integration tests for decisioning engine
    By default this file runs all suites.  But, you can isolate just one suite or even a single test within the suite
    by uncommenting the line below. Simply specify a suite filename (without extension), and a (optional) test key.
"""
# pylint: disable=cell-var-from-loop
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
import os
import unittest
import datetime
import json
from copy import deepcopy
from contextlib import contextmanager
from urllib3 import HTTPResponse
from urllib3 import PoolManager
from target_decisioning_engine.tests.helpers import expect_to_match_object
from target_decisioning_engine.tests.helpers import create_decisioning_config
from target_decisioning_engine.tests.helpers import create_target_delivery_request
from target_decisioning_engine import TargetDecisioningEngine


JUST_THIS_TEST = None
# JUST_THIS_TEST = {
#   "suite": "TEST_SUITE_TIMEFRAME",
#   "test": "friday_out_of_range"
# }

# GA TODO - uncomment this once DecisionProvider is merged
TEST_SUITES = []
# TEST_SUITES = get_test_suites(JUST_THIS_TEST.get("suite") if JUST_THIS_TEST else None)


def should_execute_test(_test_key):
    """Determines if test case should be executed"""
    return True if not JUST_THIS_TEST or not JUST_THIS_TEST.get("test") else JUST_THIS_TEST.get("test") == _test_key


@contextmanager
def datetime_mock(mock_date):
    """datetime.utcnow mock"""
    if mock_date:
        with patch("{}.datetime.datetime".format(__name__), Mock(wraps=datetime.datetime)) as mock_datetime:
            mock_datetime.utcnow.return_value = mock_date
            yield
    yield None


@contextmanager
def geo_mock(mock_geo):
    """GeoProvider http mock"""
    # GA TODO - GeoProvider - prevent this from colliding with artifact mock
    if mock_geo:
        with patch.object(PoolManager, "request", return_value=HTTPResponse(status=200, body=json.dumps(mock_geo))):
            yield
    yield None


@contextmanager
def artifact_mock(artifact):
    """ArtifactProvider http mock"""
    with patch.object(PoolManager, "request", return_value=HTTPResponse(status=200, body=json.dumps(artifact))):
        yield


@contextmanager
def combined_context(artifact, mock_date, mock_geo):
    """Combines all conditional mocks into a single context manager"""
    with artifact_mock(artifact) as artifact_context, datetime_mock(mock_date) as datetime_context, \
            geo_mock(mock_geo) as geo_context:
        yield artifact_context, datetime_context, geo_context


def get_test(_test_key, suite):
    """Returns dict with all test metadata from test file"""
    return {
        "test_description": suite.get("test", {}).get(_test_key, {}).get("description"),
        "suite_data": suite,
        "test_data": suite.get("test", {}).get(_test_key)
    }


class TestDecisioning(unittest.TestCase):
    """TestDecisioning"""

    def setUp(self):
        self.decisioning = None

    def tearDown(self):
        if self.decisioning:
            self.decisioning.stop_polling()

    # GA TODO - uncomment this once DecisionProvider is merged
    # def test_suites_exist(self):
    #     self.assertGreaterEqual(len(TEST_SUITES), 1)

    def test_run_all_tests_on_ci(self):
        if os.getenv('CI'):
            self.assertIsNone(JUST_THIS_TEST)

    def execute_test(self, _test):
        """Executes single test from suite"""
        suite_data = _test.get("suite_data")
        test_data = _test.get("test_data")
        send_notifications_fn = Mock()

        _input, output, notification_output, mock_date, mock_geo = \
            [test_data.get(key) for key in ["input", "output", "notificationOutput", "mockDate", "mockGeo"]]

        conf = test_data.get("conf") or suite_data.get("conf")
        artifact = test_data.get("artifact") or suite_data.get("artifact")

        decisioning_config = create_decisioning_config(deepcopy(conf))
        decisioning_config.send_notification_func = send_notifications_fn
        self.decisioning = TargetDecisioningEngine(decisioning_config)

        with combined_context(artifact, mock_date, mock_geo):
            self.decisioning.initialize()
            self.assertEqual(self.decisioning.get_raw_artifact(), artifact)
            get_offers_opts = create_target_delivery_request(_input)
            result = self.decisioning.get_offers(get_offers_opts)
            expect_to_match_object(result, output)

        if not notification_output:
            self.assertEqual(send_notifications_fn.call_count, 0)
        else:
            self.assertEqual(send_notifications_fn.call_count, 1)
            notification_payload = send_notifications_fn.call_args[0][0]
            expect_to_match_object(notification_payload, notification_output)


for i in range(1, len(TEST_SUITES)):
    test_suite = TEST_SUITES[i]
    SUITE_DESCRIPTION = 'test_{}'.format(test_suite.get("description"))
    for test_key in test_suite.get("test").keys():
        if should_execute_test(test_key):
            test = get_test(test_key, test_suite)


            def test_function(self):
                self.execute_test(test)


            test_description = test.get("test_description")
            TEST_NAME = "{} - {}".format(SUITE_DESCRIPTION, test_description)
            setattr(TestDecisioning, TEST_NAME, test_function)
