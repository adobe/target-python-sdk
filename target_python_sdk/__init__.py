# Copyright 2021 Adobe. All rights reserved.
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
from copy import deepcopy
from threading import Timer

from target_decisioning_engine import TargetDecisioningEngine
from target_decisioning_engine.types.decisioning_config import DecisioningConfig
from target_python_sdk.messages import MESSAGES
from target_python_sdk.validators import validate_client_options
from target_python_sdk.validators import validate_send_notifications_options
from target_python_sdk.validators import validate_get_offers_options
from target_python_sdk.helper import preserve_location_hint
from target_python_sdk.helper import request_location_hint_cookie
from target_python_sdk.target import execute_delivery
from target_python_sdk.target import handle_delivery_response
from target_tools.constants import EMPTY_REQUEST
from target_tools.attributes_provider import AttributesProvider
from target_tools.attributes_provider import get_attributes_callback
from target_tools.logger import get_logger
from target_tools.event_provider import EventProvider
from target_tools.enums import DecisioningMethod
from target_tools.utils import compose_functions
from target_tools.utils import add_mboxes_to_request
from target_tools.utils import requires_decisioning_engine

CLIENT_READY = "client_ready"
CLIENT_READY_DELAY = .1
DEFAULT_TIMEOUT = 3000
DEFAULT_OPTS = {
    "internal": True,
    "decisioning_method": DecisioningMethod.SERVER_SIDE.value
}


class TargetClient:
    """External-facing Target client for handling personalization"""

    def __init__(self, options):
        """TargetClient constructor"""
        if not options or not options.get("internal"):
            raise Exception(MESSAGES.get("PRIVATE_CONSTRUCTOR"))

        self.config = dict(options)
        self.config["timeout"] = options.get("timeout") if options.get("timeout") \
            else DEFAULT_TIMEOUT
        self.logger = get_logger(options.get("logger"))
        self.event_emitter = EventProvider(self.config.get("events")).emit
        self.decisioning_engine = None

    def initialize(self):
        """Initialize TargetClient"""
        if requires_decisioning_engine(self.config.get("decisioning_method")):
            try:
                request_location_hint_cookie(self, self.config.get("target_location_hint"))
                decisioning_config = DecisioningConfig(self.config.get("client"),
                                                       self.config.get("organization_id"),
                                                       polling_interval=self.config.get("polling_interval"),
                                                       artifact_location=self.config.get("artifact_location"),
                                                       artifact_payload=self.config.get("artifact_payload"),
                                                       environment=self.config.get("environment"),
                                                       cdn_environment=self.config.get("cdn_environment"),
                                                       cdn_base_path=self.config.get("cdn_base_path"),
                                                       send_notification_func=self.send_notifications,
                                                       telemetry_enabled=self.config.get("telemetry_enabled"),
                                                       event_emitter=self.event_emitter,
                                                       maximum_wait_ready=self.config.get("maximum_wait_ready"))
                self.decisioning_engine = TargetDecisioningEngine(decisioning_config)
                self.decisioning_engine.initialize()
                self.event_emitter(CLIENT_READY)
            except Exception as err:
                self.logger.error("Unable to initialize TargetDecisioningEngine: \n {}".format(str(err)))
        else:
            # Should emit client_ready event after client gets returned by TargetClient.create
            timer = Timer(CLIENT_READY_DELAY, self.event_emitter, [CLIENT_READY])
            timer.start()

    @staticmethod
    def create(options=None):
        """The TargetClient creation factory method
        :param options: (dict) TargetClient options, required

        options.client: (str) Target Client Id, required

        options.organization_id: (str) Target Organization Id, required

        options.timeout: (int) Target request timeout in ms, default: 3000

        options.server_domain: (str) Server domain, optional

        options.target_location_hint: (str) Target Location Hint, optional

        options.secure: (bool) Unset to enforce HTTP scheme, default: true

        options.logger: (dict) Replaces the default INFO level logger, optional

        options.decisioning_method: ("on-device"|"server-side"|"hybrid")
            The decisioning method, defaults to remote, optional

        options.polling_interval: (int) Local Decisioning -
            Polling interval in ms, default: 30000

        options.maximum_wait_ready: (int) Local Decisioning - The maximum amount of time (in ms)
            to wait for clientReady.  Default is to wait indefinitely.

        options.artifact_location: (str) Local Decisioning - Fully qualified url to the location
            of the artifact, optional

        options.artifact_payload: (target_decisioning_engine.types.decisioning_artifact.DecisioningArtifact)
            Local Decisioning - A pre-fetched artifact, optional

        options.environment_id: (int) The Target environment ID, defaults to production, optional

        options.environment: (str) The Target environment name, defaults to production, optional

        options.cdn_environment: (str) The CDN environment name, defaults to production, optional

        options.telemetry_enabled: (bool) - If set to false, telemetry data will not be sent to Adobe

        options.version: (str) - The version number of this sdk, optional

        options.property_token: (str) - A property token used to limit the scope of evaluated target
            activities, optional

        options.events: (dict.<str, callable>) An object with event name keys and callback
            function values, optional

        :return TargetClient instance object
        """

        error = validate_client_options(options)

        if error:
            raise Exception(error)

        opts = dict(DEFAULT_OPTS)
        opts.update(options)
        client = TargetClient(opts)
        client.initialize()
        return client

    def get_offers(self, options):
        """Fetches personalization offers
        :param options: (dict) Request options

        options.request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
            Target View Delivery API request, required

        options.target_cookie: (str) Target cookie, optional

        options.target_location_hint: (str) Target Location Hint, optional

        options.consumer_id: (str) When stitching multiple calls, different consumerIds should be provided, optional

        options.customer_ids: (list) A list of Customer Ids in VisitorId-compatible format, optional

        options.session_id: (str) Session Id, used for linking multiple requests, optional

        options.decisioning_method: ("on-device"|"server-side"|"hybrid") Execution mode, defaults to remote, optional

        options.callback: (callable) If handling request asynchronously, the callback is invoked when response is ready

        options.err_callback: (callable) If handling request asynchronously, error callback is invoked when exception
            is raised
        :return (target_python_sdk.types.target_delivery_response.TargetDeliveryResponse)
            Returns response synchronously if no options.callback provided, otherwise returns AsyncResult.
            If callback was provided then a DeliveryResponse will be returned through that.
        """

        error = validate_get_offers_options(options)

        if error:
            raise Exception(error)

        config = deepcopy(self.config)
        config["decisioning_method"] = options.get("decisioning_method") or self.config.get("decisioning_method")
        target_options = {
            "config": config
        }
        target_options.update(options)
        return execute_delivery(self.config, target_options, self.decisioning_engine)

    def send_notifications(self, options):
        """ The TargetClient sendNotifications method
        :param options: (dict) Notifications request options

        options.request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
            Target View Delivery API request, required

        options.target_cookie: (str) Target cookie, optional

        options.target_location_hint: (str) Target Location Hint, optional

        options.consumer_id: (str) When stitching multiple calls, different consumerIds should be provided, optional

        options.customer_ids: (list) A list of Customer Ids in VisitorId-compatible format, optional

        options.session_id: (str) Session Id, used for linking multiple requests, optional

        options.callback: (callable) If handling request asynchronously, the callback is invoked when response is ready

        options.err_callback: (callable) If handling request asynchronously, error callback is invoked when exception
            is raised

        :return (target_python_sdk.types.target_delivery_response.TargetDeliveryResponse)
            Returns response synchronously if no options.callback provided, otherwise returns AsyncResult.
            If callback was provided, then a DeliveryResponse will be returned through that.
        """

        error = validate_send_notifications_options(options)

        if error:
            raise Exception(error)

        config = deepcopy(self.config)
        # execution mode for sending notifications must always be remote
        config["decisioning_method"] = DecisioningMethod.SERVER_SIDE.value
        target_options = {
            "config": config
        }
        target_options.update(options)
        return execute_delivery(self.config, target_options)

    def get_attributes(self, mbox_names, options=None):
        """
        The TargetClient get_attributes method
        :param mbox_names: (list) A list of mbox names that contains JSON content attributes, required
        :param options: (dict) Request options
        options.request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
            Target View Delivery API request, required
        options.target_cookie: (str) Target cookie, optional
        options.target_location_hint: (str) Target Location Hint, optional
        options.consumer_id: (str) When stitching multiple calls, different consumerIds should be provided, optional
        options.customer_ids: (list) A list of Customer Ids in VisitorId-compatible format, optional
        options.session_id: (str) Session Id, used for linking multiple requests, optional
        options.decisioning_method: ("on-device"|"server-side"|"hybrid") Execution mode, defaults to remote, optional
        options.callback: (callable) If handling request asynchronously, the callback is invoked when response is ready
        options.err_callback: (callable) If handling request asynchronously, error callback is invoked when exception
            is raised
        :return (target_tools.attributes_provider.AttributesProvider|AsyncResult)
            Returns AttributesProvider synchronously if no options.callback provided, otherwise returns AsyncResult.
            If callback was provided then an AttributesProvider will be returned through that
        """

        if not options or not options.get("request"):
            options = {"request": EMPTY_REQUEST}

        add_mboxes_to_request(
            mbox_names, options.get("request"), "execute")

        if options.get("callback"):
            wrapped_callback = compose_functions(options.get("callback"), get_attributes_callback)
            options["callback"] = wrapped_callback
            return self.get_offers(options)

        response = self.get_offers(options)
        return AttributesProvider(response)
