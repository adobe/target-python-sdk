# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""DecisioningConfig model"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-few-public-methods


class DecisioningConfig:
    """DecisioningConfig"""

    def __init__(self, client, organization_id, polling_interval=None,
                 artifact_location=None, artifact_payload=None, property_token=None, environment=None,
                 cdn_environment=None, cdn_base_path=None, logger=None, send_notification_func=None,
                 telemetry_enabled=True, event_emitter=None, maximum_wait_ready=None):
        self.client = client
        self.organization_id = organization_id
        self.polling_interval = polling_interval
        self.artifact_location = artifact_location
        self.artifact_payload = artifact_payload
        self.property_token = property_token
        self.environment = environment
        self.cdn_environment = cdn_environment
        self.cdn_base_path = cdn_base_path
        self.logger = logger
        self.send_notification_func = send_notification_func
        self.telemetry_enabled = telemetry_enabled
        self.event_emitter = event_emitter if event_emitter and callable(event_emitter) else \
            lambda event_name, payload: None
        self.maximum_wait_ready = maximum_wait_ready
