# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Util functions for testing decisioning engine"""
# pylint: disable=unused-argument
import os
from target_python_sdk.utils import is_dict
from target_python_sdk.utils import is_string
from target_python_sdk.utils import is_number
from target_python_sdk.utils import is_list
from target_python_sdk.tests.helpers import read_json_file
from target_python_sdk.tests.delivery_request_setup import create_delivery_request
from target_decisioning_engine.types.decisioning_config import DecisioningConfig
from target_decisioning_engine.types.target_delivery_request import TargetDeliveryRequest


CURRENT_DIR = os.path.dirname(__file__)
TEST_ARTIFACTS_FOLDER = os.path.join(CURRENT_DIR, "schema/artifacts")
TEST_MODELS_FOLDER = os.path.join(CURRENT_DIR, "schema/models")


def _default_parse_handler(key, value):
    """Default parse handler for object traversal"""
    return value


def _traverse_object(obj=None, result=None, parse_handler=_default_parse_handler):
    """Traverses dict obj and constructs a new dict by executing parse_handler for each dict entry"""
    if is_dict(result):
        for key, val in obj.items():
            if is_list(val) or is_dict(val):
                result[key] = _traverse_object(val, [] if is_list(val) else {}, parse_handler)
            else:
                result[key] = parse_handler(key, val)
    elif is_list(result):
        for key, val in enumerate(obj):
            if is_list(val) or is_dict(val):
                result.append(_traverse_object(val, [] if is_list(val) else {}, parse_handler))
            else:
                result.append(parse_handler(key, val))

    return result


def assert_object(value):
    """Throws AssertionError if value is not an object"""
    assert isinstance(value, object), "'{}' is not an object".format(value)


def assert_string(value):
    """Throws AssertionError if value is not a str"""
    assert is_string(value), "'{}' is not a string".format(value)


def assert_number(value):
    """Throws AssertionError if value is not an int"""
    assert is_number(value), "'{}' is not a number".format(value)


def prepare_test_response(response=None):
    """Traverses expected response and sets custom matchers for dynamic values"""
    if not response:
        response = {}

    specials = {
        "expect.any(Object)": assert_object,
        "expect.any(String)": assert_string,
        "expect.any(Number)": assert_number
    }

    def _special_value_handler(key, value):
        """Gets custom matcher function"""
        return specials.get(value, value)

    return _traverse_object(response, {}, _special_value_handler)


def _hydrate_artifacts(artifact_folder, artifact_list, test_obj=None):
    """Traverses test_obj and replaces artifact name with actual artifact json"""
    if not test_obj:
        test_obj = {}

    def _artifact_handler(key, value):
        """Replaces artifact name with actual artifact json"""
        if key == "artifact":
            artifact_filename = "{}.json".format(value)
            if artifact_filename not in artifact_list:
                return value

            return read_json_file(artifact_folder, artifact_filename)

        return value

    return _traverse_object(test_obj, {}, _artifact_handler)


def expect_to_match_object(received, expected):
    """Validates received response against expected response"""
    expected = prepare_test_response(expected)

    if received is None:
        assert expected is None, "None value received, but expected '{}'".format(expected)

    for key, value in expected.items():
        if callable(value):
            value(received.get(key))
        elif is_dict(value):
            expect_to_match_object(received.get(key), value)
        elif is_list(value):
            for index, item in enumerate(value):
                if is_dict(item):
                    received_item = received.get(key)[index] if received.get(key) else {}
                    expect_to_match_object(received_item, item)
                else:
                    assert item == received.get(key)[index], \
                        "Received list item '{}' does not equal expected list item '{}'" \
                        .format(str(received.get(key)[index]), str(item))
        else:
            assert value == received.get(key), \
                "Received value '{}' for key '{}' does not equal expected value '{}'" \
                .format(received.get(key), key, value)


def is_json(filename):
    """Predicate for checking if a filename is .json"""
    return filename.lower().endswith(".json")


def get_files_in_dir(directory):
    """Lists all files in a given directory"""
    return [filename for filename in os.listdir(directory) if os.path.isfile(os.path.join(directory, filename))]


def get_test_artifacts():
    """Retrieves all json filenames from the artifacts directory
    :return (iterable<str>)
    """
    return filter(is_json, get_files_in_dir(TEST_ARTIFACTS_FOLDER))


def get_test_models():
    """Retrieves all json filenames from the models directory (returns iterable)
    :return (iterable<str>)
    """
    return filter(is_json, get_files_in_dir(TEST_MODELS_FOLDER))


def get_test_suites(test_suite_name, exclude_suites):
    """Retrieves and hydrates all artifacts.  Filters by test suite if test_suite_name provided"""
    artifacts = list(get_test_artifacts())
    test_models = get_test_models()

    def _matches_test_suite_name(filename):
        """Checks if filename matches test_suite_name"""
        return True if not test_suite_name else filename == "{}.json".format(test_suite_name)

    hydrated_artifacts = []
    for test_model_file_name in test_models:
        if not _matches_test_suite_name(test_model_file_name) or test_model_file_name in exclude_suites:
            continue
        suite = read_json_file(TEST_MODELS_FOLDER, test_model_file_name)
        hydrated_artifacts.append(_hydrate_artifacts(TEST_ARTIFACTS_FOLDER, artifacts, suite))
    return hydrated_artifacts


def create_decisioning_config(config_dict):
    """Converts dict representation of decisioning config to DecisioningConfig object"""
    return DecisioningConfig(config_dict.get("client"),
                             config_dict.get("organizationId"),
                             polling_interval=config_dict.get("pollingInterval"),
                             artifact_location=config_dict.get("artifactLocation"),
                             artifact_payload=config_dict.get("artifactPayload"),
                             environment=config_dict.get("environment"),
                             cdn_environment=config_dict.get("cdn_environment"),
                             cdn_base_path=config_dict.get("cdnBasePath"),
                             send_notification_func=config_dict.get("sendNotificationFunc"),
                             telemetry_enabled=config_dict.get("telemetryEnabled"),
                             event_emitter=config_dict.get("eventEmitter"),
                             maximum_wait_ready=config_dict.get("maximumWaitReady"))


def create_target_delivery_request(get_offers_opts):
    """Converts dict representation of get_offers options to TargetDeliveryRequest object"""
    return TargetDeliveryRequest(request=create_delivery_request(get_offers_opts.get("request")),
                                 visitor_cookie=get_offers_opts.get("visitorCookie"),
                                 target_cookie=get_offers_opts.get("targetCookie"),
                                 target_location_hint=get_offers_opts.get("targetLocationHint"),
                                 consumer_id=get_offers_opts.get("consumerId"),
                                 customer_ids=get_offers_opts.get("customerIds"),
                                 session_id=get_offers_opts.get("sessionId"),
                                 visitor=get_offers_opts.get("visitor"))
