# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Util functions for testing decisioning engine"""
import os
from target_tools.tests.helpers import is_json
from target_tools.tests.helpers import traverse_object
from target_tools.tests.helpers import read_json_file
from target_tools.tests.delivery_request_setup import create_delivery_request
from target_decisioning_engine.types.decisioning_config import DecisioningConfig
from target_decisioning_engine.types.target_delivery_request import TargetDeliveryRequest


CURRENT_DIR = os.path.dirname(__file__)
TEST_ARTIFACTS_FOLDER = os.path.join(CURRENT_DIR, "schema/artifacts")
TEST_MODELS_FOLDER = os.path.join(CURRENT_DIR, "schema/models")


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

    return traverse_object(test_obj, {}, _artifact_handler)


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
