# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""
This module includes the TargetClient for making personalization requests
"""
from threading import Timer
from target_python_sdk.messages import MESSAGES
from target_python_sdk.events import CLIENT_READY
from target_python_sdk.validators import validate_client_options
from target_python_sdk.enums import DecisioningMethod
from target_tools.logger import get_logger
from target_tools.event_provider import EventProvider
from target_tools.networking import get_fetch_api

CLIENT_READY_DELAY = .1
DEFAULT_TIMEOUT = 3000
DEFAULT_OPTS = {
    'internal': True,
    'decisioningMethod': DecisioningMethod.SERVER_SIDE
}


class TargetClient:
    """External-facing Target client for handling personalization"""
    def __init__(self, options):
        if not options or not options.get('internal'):
            raise Exception(MESSAGES.get('PRIVATE_CONSTRUCTOR'))

        self.config = options
        self.config['timeout'] = options.get('timeout') if options.get('timeout') \
            else DEFAULT_TIMEOUT
        self.logger = get_logger(options.get('logger'))
        event_emitter = EventProvider(self.config.get('events')).emit

        timer = Timer(CLIENT_READY_DELAY, event_emitter, [CLIENT_READY])
        timer.start()

    @staticmethod
    def create(options=None):
        """
        The TargetClient creation factory method
        :parameter
        options: dict - TargetClient options, required
        options.fetch_api: function - Fetch Implementation, optional
        options.client: str - Target Client Id, required
        options.organization_id: str - Target Organization Id, required
        options.timeout: int - Target request timeout in ms, default: 3000
        options.server_domain: str - Server domain, optional
        options.target_location_hint: str - Target Location Hint, optional
        options.secure: bool - Unset to enforce HTTP scheme, default: true
        options.logger: dict - Replaces the default noop logger, optional
        options.decisioning_method: str ('on-device'|'server-side'|'hybrid')
            - The decisioning method, defaults to remote, optional
        options.polling_interval: int - (Local Decisioning)
            Polling interval in ms, default: 30000
        options.maximum_wait_ready: int - (Local Decisioning) The maximum amount of time (in ms)
            to wait for clientReady.  Default is to wait indefinitely.
        options.artifact_location: str - (Local Decisioning) Fully qualified url to the location
            of the artifact, optional
        options.artifact_payload: str
            "import("@adobe/target-decisioning-engine/types/DecisioningArtifact")
            .DecisioningArtifact" - (Local Decisioning) A pre-fetched artifact, optional
        options.environment_id: int - The Target environment ID, defaults to production, optional
        options.environment: str - The Target environment name, defaults to production, optional
        options.cdn_environment: str - The CDN environment name, defaults to production, optional
        options.telemetry_enabled: bool - If set to false, telemetry data will not be sent to Adobe
        options.version: str - The version number of at.js, optional
        options.property_token: str - A property token used to limit the scope of evaluated target
            activities, optional
        options.events: dict.<str, function> - An object with event name keys and callback
            function values, optional
        :returns
        TargetClient instance object
        """

        error = validate_client_options(options)

        if error:
            raise Exception(error)

        fetch_impl = get_fetch_api(options.get('fetch_api'))
        options['fetch_api'] = fetch_impl

        opts = dict(DEFAULT_OPTS)
        opts.update(options)
        return TargetClient(opts)

    def get_offers(self, options):
        """Fetches personalization offers"""
