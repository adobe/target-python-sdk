# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""DecisioningConfig model"""


class DecisioningConfig:
    """DecisioningConfig"""

    def __init__(self, client, organization_id, polling_interval=None,
                 artifact_location=None, artifact_payload=None, environment=None,
                 cdn_environment=None, cdn_base_path=None, send_notification_func=None,
                 telemetry_enabled=True, event_emitter=None, maximum_wait_ready=None):
        """
        :param client: (str) Target Client Id
        :param organization_id: (str) Target Organization Id
        :param polling_interval: (int) Polling interval in seconds, default: 300
        :param artifact_location: (str) Fully qualified url to the location of the artifact
        :param artifact_payload: (dict) A pre-fetched artifact
        :param environment: ("production"|"staging"|"development") The target environment name. Defaults to production.
        :param cdn_environment: ("production"|"staging"|"development") The CDN environment name. Defaults to production
        :param cdn_base_path: (str) A CDN base URL to override the default based on cdnEnvironment.
        :param send_notification_func: (callable) Function used to send notifications
        :param telemetry_enabled: (bool) If set to false, telemetry data will not be sent to Adobe
        :param event_emitter: (callable) Function used to emit events
        :param maximum_wait_ready: (int) The maximum amount of time (in seconds) to wait for decisioning engine to
            become ready.  Default is to wait indefinitely.
        """
        self.client = client
        self.organization_id = organization_id
        self.polling_interval = polling_interval
        self.artifact_location = artifact_location
        self.artifact_payload = artifact_payload
        self.environment = environment
        self.cdn_environment = cdn_environment
        self.cdn_base_path = cdn_base_path
        self.send_notification_func = send_notification_func
        self.telemetry_enabled = telemetry_enabled
        self.event_emitter = event_emitter if event_emitter and callable(event_emitter) else \
            lambda event_name, payload: None
        self.maximum_wait_ready = maximum_wait_ready
