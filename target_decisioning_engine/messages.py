# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Error and log messages for On Device Decisioning"""


def error_max_retry(num_retries, err_string):
    """error_max_retry message"""
    return "Unable to retrieve artifact after {} retries: {}".format(num_retries, err_string)


def artifact_version_unsupported(artifact_version, supported_major_version):
    """artifact_version_unsupported message"""
    return "The decisioning artifact version ({}) is not supported. " \
           "This library is compatible with this major version: " \
           "{}".format(artifact_version, supported_major_version)


def artifact_fetch_error(reason):
    """artifact_fetch_error message"""
    return"Failed to retrieve artifact: {}".format(reason)


def invalid_environment(expected_environment, default_environment):
    """invalid_environment message"""
    return "'{}' is not a valid target environment, defaulting to '{}'."\
        .format(expected_environment, default_environment)


MESSAGES = {
    "ERROR_MAX_RETRY": error_max_retry,
    "ARTIFACT_NOT_AVAILABLE": "The decisioning artifact is not available",
    "ARTIFACT_VERSION_UNSUPPORTED": artifact_version_unsupported,
    "ARTIFACT_FETCH_ERROR": artifact_fetch_error,
    "ARTIFACT_INVALID": "Invalid Artifact",
    "INVALID_ENVIRONMENT": invalid_environment,
    "NOT_APPLICABLE": "Not Applicable",
    "ARTIFACT_OBFUSCATION_ERROR": "Unable to read artifact JSON",
    "UNKNOWN": "unknown"
}
