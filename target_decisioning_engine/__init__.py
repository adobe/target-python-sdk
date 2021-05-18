# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""TargetDecisioningEngine"""
from copy import deepcopy
from target_decisioning_engine import artifact_provider
from target_decisioning_engine.artifact_provider import ArtifactProvider
from target_decisioning_engine.constants import SUPPORTED_ARTIFACT_MAJOR_VERSION
from target_decisioning_engine.context_provider import create_decisioning_context
from target_decisioning_engine.messages import MESSAGES
from target_decisioning_engine.request_provider import valid_delivery_request
from target_decisioning_engine.utils import match_major_version
from target_decisioning_engine.utils import has_remote_dependency
from target_decisioning_engine.decision_provider import DecisionProvider
from target_decisioning_engine.geo_provider import GeoProvider
from target_decisioning_engine.trace_provider import TraceProvider


class TargetDecisioningEngine:
    """TargetDecisioningEngine"""

    def __init__(self, config):
        """
        :param config: (target_decisioning_engine.types.decisioning_config.DecisioningConfig)
        """
        self.config = config
        self._artifact_provider = None
        self.artifact = None

    def get_offers(self, target_options):
        """
        :param target_options: (target_decisioning_engine.types.target_delivery_request.TargetDeliveryRequest)
        :return: (dict) get offers response
        """
        request = target_options.request
        if not self.artifact:
            raise Exception(MESSAGES.get("ARTIFACT_NOT_AVAILABLE"))

        if not match_major_version(self.artifact.get("version"), SUPPORTED_ARTIFACT_MAJOR_VERSION):
            raise Exception(MESSAGES.get("ARTIFACT_VERSION_UNSUPPORTED")(
                self.artifact.get("version"),
                SUPPORTED_ARTIFACT_MAJOR_VERSION)
            )

        _geo_provider = GeoProvider(self.config, self.artifact)
        valid_request = valid_delivery_request(request, target_options.target_location_hint,
                                               _geo_provider.valid_geo_request_context)

        options = deepcopy(target_options)
        options.request = valid_request

        _trace_provider = TraceProvider(self.config, options, self._artifact_provider.get_trace())

        decisioning = DecisionProvider(self.config, options, create_decisioning_context(valid_request),
                                       self.artifact, _trace_provider)
        return decisioning.run()

    def is_ready(self):
        """
        :return: (bool) Returns True if artifact has been fetched, False otherwise
        """
        return bool(self.artifact)

    def get_raw_artifact(self):
        """
        :return: (target_decisioning_engine.types.decisioning_artifact.DecisioningArtifact)
        """
        return self.artifact

    def stop_polling(self):
        """Stops artifact polling"""
        self._artifact_provider.stop_polling()

    def has_remote_dependency(self, request):
        """
        :param request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
            Target Delivery API request, required
        :return: (dict) items with remote dependencies
        """
        return has_remote_dependency(self.artifact, request)

    def initialize(self):
        """Initializes TargetDecisioningEngine.  Must be called in order to start artifact polling"""
        self._artifact_provider = ArtifactProvider(self.config)
        self._artifact_provider.initialize()
        self.artifact = self._artifact_provider.get_artifact()

        if not self.artifact:
            raise Exception(MESSAGES.get("ARTIFACT_NOT_AVAILABLE"))

        def _artifact_subscriber(data):
            self.artifact = data

        # subscribe to new artifacts that are downloaded on the polling interval
        self._artifact_provider.subscribe(_artifact_subscriber)
