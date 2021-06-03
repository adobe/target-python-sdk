# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""On Device Decisioning Artifact Provider"""
import json
from threading import Timer
import urllib3
from urllib3 import Retry
from target_decisioning_engine.constants import LOG_PREFIX
from target_decisioning_engine.constants import FORBIDDEN
from target_decisioning_engine.constants import HTTP_GET
from target_decisioning_engine.constants import NOT_MODIFIED
from target_decisioning_engine.constants import OK
from target_decisioning_engine.constants import MINIMUM_POLLING_INTERVAL
from target_decisioning_engine.constants import DEFAULT_POLLING_INTERVAL
from target_decisioning_engine.constants import NUM_FETCH_RETRIES
from target_decisioning_engine.events import ARTIFACT_DOWNLOAD_SUCCEEDED
from target_decisioning_engine.events import GEO_LOCATION_UPDATED
from target_decisioning_engine.events import ARTIFACT_DOWNLOAD_FAILED
from target_decisioning_engine.messages import MESSAGES
from target_decisioning_engine.timings import TIMING_ARTIFACT_READ_JSON
from target_decisioning_engine.timings import TIMING_ARTIFACT_DOWNLOADED_TOTAL
from target_decisioning_engine.timings import TIMING_ARTIFACT_DOWNLOADED_FETCH
from target_decisioning_engine.timings import TIMING_ARTIFACT_GET_INITIAL
from target_decisioning_engine.trace_provider import ArtifactTracer
from target_decisioning_engine.utils import determine_artifact_location
from target_decisioning_engine.utils import get_http_codes_to_retry
from target_decisioning_engine.geo_provider import create_or_update_geo_object
from target_tools.utils import is_int
from target_tools.utils import to_dict
from target_tools.utils import is_string
from target_tools.utils import is_dict
from target_tools.logger import get_logger
from target_tools.perf_tool import get_perf_tool_instance
from target_tools.utils import noop

LOG_TAG = "{}.ArtifactProvider".format(LOG_PREFIX)
BACKOFF_FACTOR = 0.1
CODES_TO_RETRY = get_http_codes_to_retry()


def get_min_polling_interval():
    """Minimum allowed amount of time between polling - in seconds"""
    return MINIMUM_POLLING_INTERVAL


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
        self.logger = get_logger()
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
        self.perf_tool = get_perf_tool_instance()

    def _get_polling_interval(self):
        """Get artifact polling interval"""
        if self.config.polling_interval == 0:
            return 0

        return max(
            get_min_polling_interval(),
            self.config.polling_interval if is_int(self.config.polling_interval) else DEFAULT_POLLING_INTERVAL
        )

    def initialize(self):
        """Initialize ArtifactProvider and fetch initial artifact"""
        self.polling_interval = self._get_polling_interval()
        self.artifact_location = self.config.artifact_location if is_string(self.config.artifact_location) else \
            determine_artifact_location(self.config)
        try:
            self.artifact = self._get_initial_artifact()
            self.artifact_tracer = ArtifactTracer(
                self.artifact_location,
                self.config.artifact_payload,
                self.polling_interval,
                self.polling_halted,
                self.artifact
            )
            self.subscribe(self._artifact_tracer_update)
        finally:
            self._schedule_next_update()

    def _emit_new_artifact(self, artifact_payload, geo_context=None):
        """Send events and notify subscribers of new artifact
        :param artifact_payload: (dict) artifact payload in dict format
        :param geo_context: (dict) geo object in dict format
        :return: None
        """
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

    def subscribe(self, callback_func):
        """Add event subscription"""
        self.subscription_count += 1
        self.subscriptions[self.subscription_count] = callback_func
        return self.subscription_count

    def unsubscribe(self, _id):
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

    def stop_polling(self):
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
        self.perf_tool.time_start(TIMING_ARTIFACT_GET_INITIAL)
        artifact = self.config.artifact_payload if is_dict(self.config.artifact_payload) else \
            self._fetch_artifact(self.artifact_location)
        self.perf_tool.time_end(TIMING_ARTIFACT_GET_INITIAL)
        return artifact

    def _artifact_tracer_update(self, artifact):
        """Update ArtifactTracer with latest artifact"""
        self.artifact_tracer.provide_new_artifact(artifact)

    def get_trace(self):
        """Returns ArtifactTracer in dict format"""
        return self.artifact_tracer.to_dict()

    def _fetch_artifact(self, artifact_url):
        """Fetch artifact from server"""
        self.perf_tool.time_start(TIMING_ARTIFACT_DOWNLOADED_TOTAL)
        headers = {}
        self.logger.debug("{} fetching artifact - {}".format(LOG_TAG, artifact_url))

        if self.last_response_etag:
            headers["If-None-Match"] = self.last_response_etag

        try:
            self.perf_tool.time_start(TIMING_ARTIFACT_DOWNLOADED_FETCH)
            res = self.pool_manager.request(HTTP_GET, artifact_url, headers=headers, retries=self.http_retry)
            self.perf_tool.time_end(TIMING_ARTIFACT_DOWNLOADED_FETCH)
            self.logger.debug("{} artifact received - status={}".format(LOG_TAG, res.status))

            if res.status == NOT_MODIFIED and self.last_response_data:
                return self.last_response_data

            if res.status == FORBIDDEN:
                raise Exception("Artifact request is not authorized. This is likely due to On-Device-Decisioning "
                                "being disabled in Admin settings.  Please enable and try again.")

            if res.status != OK:
                raise Exception("Non-200 status code response from artifact request: {}".format(res.status))

            self.perf_tool.time_start(TIMING_ARTIFACT_READ_JSON)
            response_data = json.loads(res.data)
            self.perf_tool.time_end(TIMING_ARTIFACT_READ_JSON)
            etag = res.headers.get("Etag")
            if etag:
                self.last_response_data = response_data
                self.last_response_etag = etag

            geo = create_or_update_geo_object(geo_data=res.headers)
            self._emit_new_artifact(response_data, to_dict(geo))

            self.perf_tool.time_end(TIMING_ARTIFACT_DOWNLOADED_TOTAL)
            return response_data
        except Exception as err:
            self.logger.error(MESSAGES.get("ARTIFACT_FETCH_ERROR")(str(err)))
            failure_event = {
                "artifact_location": artifact_url,
                "error": err
            }
            self.event_emitter(ARTIFACT_DOWNLOAD_FAILED, failure_event)
        return None
