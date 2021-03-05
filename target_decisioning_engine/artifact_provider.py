# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""On Device Decisioning Artifact Provider"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=broad-except

import json
from threading import Timer
import urllib3
from urllib3 import Retry
from target_decisioning_engine.constants import LOG_PREFIX
from target_decisioning_engine.constants import MINIMUM_POLLING_INTERVAL
from target_decisioning_engine.constants import DEFAULT_POLLING_INTERVAL
from target_decisioning_engine.constants import NUM_FETCH_RETRIES
from target_decisioning_engine.events import ARTIFACT_DOWNLOAD_SUCCEEDED
from target_decisioning_engine.events import GEO_LOCATION_UPDATED
from target_decisioning_engine.events import ARTIFACT_DOWNLOAD_FAILED
from target_decisioning_engine.messages import MESSAGES
from target_decisioning_engine.utils import determine_artifact_location
from target_decisioning_engine.utils import get_http_codes_to_retry
from target_python_sdk.utils import is_number
from target_python_sdk.utils import is_string
from target_python_sdk.utils import is_dict
from target_tools.logger import get_logger
from target_tools.utils import noop

LOG_TAG = "{}.ArtifactProvider".format(LOG_PREFIX)
NOT_MODIFIED = 304
OK = 200
HTTP_GET = "GET"
BACKOFF_FACTOR = 0.1
CODES_TO_RETRY = get_http_codes_to_retry()


class ArtifactProvider:
    """ArtifactProvider"""

    def __init__(self, config):
        """
        :param config: (target_decisioning_engine.types.decisioning_config.DecisioningConfig)
            Decisioning engine configuration
        """
        self.pool_manager = urllib3.PoolManager()
        self.http_retry = Retry(total=NUM_FETCH_RETRIES, backoff_factor=BACKOFF_FACTOR, status_forcelist=CODES_TO_RETRY)
        self.config = config
        self.logger = get_logger(config.logger)
        self.event_emitter = config.event_emitter or noop
        self.polling_interval = None
        self.artifact_location = None
        self.polling_halted = False
        self.polling_timer = None
        self.artifact = None
        self.subscriptions = {}
        self.subscription_count = 0
        self.last_response_etag = None
        self.last_response_data = None
        self.artifact_tracer = None

    def _get_polling_interval(self):
        """Get artifact polling interval"""
        if self.config.polling_interval == 0:
            return 0

        return max(
            MINIMUM_POLLING_INTERVAL,
            self.config.polling_interval if is_number(self.config.polling_interval) else DEFAULT_POLLING_INTERVAL
        )

    def initialize(self):
        """Initialize ArtifactProvider and fetch initial artifact"""
        self.polling_interval = self._get_polling_interval()
        self.artifact_location = self.config.artifact_location if is_string(self.config.artifact_location) else \
            determine_artifact_location(self.config)
        try:
            self.artifact = self._get_initial_artifact()
            # GA TODO - ArtifactTracer is a separate ticket
            # self.artifact_tracer = ArtifactTracer(
            #     self.artifact_location,
            #     self.config.artifact_payload,
            #     self.polling_interval,
            #     self.polling_halted,
            #     self.artifact
            # )
            # self.add_subscription(self.artifact_tracer_update)
        finally:
            self._schedule_next_update()

    def _emit_new_artifact(self, artifact_payload, geo_context=None):
        """Send events and notify subscribers of new artifact"""
        if not geo_context:
            geo_context = {}

        self.event_emitter(ARTIFACT_DOWNLOAD_SUCCEEDED, {
            "artifact_location": self.artifact_location,
            "artifact_payload": artifact_payload
        })

        self.event_emitter(GEO_LOCATION_UPDATED, {
            "geo_context": geo_context
        })

        for subscription_func in self.subscriptions.values():
            subscription_func(artifact_payload)

    def add_subscription(self, callback_func):
        """Add event subscription"""
        self.subscription_count += 1
        self.subscriptions[self.subscription_count] = callback_func
        return self.subscription_count

    def remove_subscription(self, _id):
        """Remove event subscription"""
        try:
            del self.subscriptions[_id]
            self.subscription_count -= 1
        except KeyError:
            pass

    def _fetch_and_schedule(self):
        """Fetch artifact and schedule next polling"""
        self.artifact = self._fetch_artifact(self.artifact_location)
        self._schedule_next_update()

    def _schedule_next_update(self):
        """Schedule next artifact polling based on configured interval (in seconds)"""
        if self.polling_interval == 0 or self.polling_halted:
            return

        self.polling_timer = Timer(self.polling_interval, self._fetch_and_schedule)
        self.polling_timer.start()

    def stop_all_polling(self):
        """Disable artifact polling"""
        if self.polling_timer:
            self.polling_timer.cancel()
            self.polling_timer = None
        self.polling_halted = True

    def resume_polling(self):
        """Enable artifact polling"""
        self.polling_halted = False
        self._schedule_next_update()

    def get_artifact(self):
        """Return current artifact"""
        return self.artifact

    def _get_initial_artifact(self):
        """Fetch initial artifact"""
        return self.config.artifact_payload if is_dict(self.config.artifact_payload) else \
            self._fetch_artifact(self.artifact_location)

    def _artifact_tracer_update(self, artifact):
        """Update ArtifactTracer with latest artifact"""
        self.artifact_tracer.provide_new_artifact(artifact)

    def _fetch_artifact(self, artifact_url):
        """Fetch artifact from server"""
        headers = {}
        self.logger.debug("{} fetching artifact - {}".format(LOG_TAG, artifact_url))

        if self.last_response_etag:
            headers["If-None-Match"] = self.last_response_etag

        try:
            res = self.pool_manager.request(HTTP_GET, artifact_url, headers=headers, retries=self.http_retry)
            self.logger.debug("{} artifact received - status={}".format(LOG_TAG, res.status))

            if res.status == NOT_MODIFIED and self.last_response_data:
                return self.last_response_data

            if res.status == OK:
                response_data = json.loads(res.data)
                etag = res.headers.get("Etag")
                if etag:
                    self.last_response_data = response_data
                    self.last_response_etag = etag

                # GA TODO - GeoProvider separate ticket + add test to make sure _emit_new_artifact called
                # self._emit_new_artifact(response_data, create_geo_object_from_headers(res.headers))
                self._emit_new_artifact(response_data)

                return response_data
        except Exception as err:
            self.logger.error(MESSAGES.get("ARTIFACT_FETCH_ERROR")(str(err)))
            failure_event = {
                "artifact_location": artifact_url,
                "error": err
            }
            self.event_emitter(ARTIFACT_DOWNLOAD_FAILED, failure_event)
        return None
