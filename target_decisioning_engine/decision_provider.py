# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""DecisionProvider for on-device decisioning"""
# pylint: disable=too-many-statements
try:
    from functools import reduce
except ImportError:
    pass
from delivery_api_client import MboxResponse
from delivery_api_client import TelemetryEntry
from delivery_api_client import MboxRequest
from delivery_api_client import ExecuteResponse
from delivery_api_client import PrefetchResponse
from target_decisioning_engine.constants import LOG_PREFIX
from target_decisioning_engine.enums import RequestType
from target_decisioning_engine.post_processors import remove_page_load_attributes
from target_decisioning_engine.post_processors import prepare_execute_response
from target_decisioning_engine.post_processors import prepare_prefetch_response
from target_decisioning_engine.post_processors import create_response_tokens_post_processor
from target_decisioning_engine.post_processors import replace_campaign_macros
from target_decisioning_engine.post_processors import add_trace
from target_decisioning_engine.filters import by_property_token
from target_decisioning_engine.rule_evaluator import RuleEvaluator
from target_decisioning_engine.timings import TIMING_GET_OFFER
from target_decisioning_engine.types.decision_provider_response import DecisionProviderResponse
from target_decisioning_engine.utils import has_remote_dependency
from target_decisioning_engine.utils import get_rule_key
from target_decisioning_engine.notification_provider import NotificationProvider
from target_decisioning_engine.trace_provider import RequestTracer
from target_tools.utils import flatten_list
from target_tools.constants import DEFAULT_GLOBAL_MBOX
from target_tools.logger import get_logger
from target_tools.utils import get_property_token
from target_tools.perf_tool import get_perf_tool_instance

LOG_TAG = "{}.DecisionProvider".format(LOG_PREFIX)
PARTIAL_CONTENT = 206
OK = 200

logger = get_logger()


def order_by_name(obj):
    """Sort by name for MboxResponse and View"""
    return obj.name


def order_by_event_token(metric):
    """Sort by event_token for Metric"""
    return metric.event_token


class DecisionProvider:
    """DecisionProvider"""

    def __init__(self, config, target_options, context, artifact, trace_provider):
        """
        :param config: (target_decisioning_engine.types.decisioning_config.DecisioningConfig) config
        :param target_options: (target_decisioning_engine.types.target_delivery_request.TargetDeliveryRequest)
            request options
        :param context: (target_decisioning_engine.types.decisioning_context.DecisioningContext) context
        :param artifact: (target_decisioning_engine.types.decisioning_artifact.DecisioningArtifact) artifact
        :param trace_provider: (target_decisioning_engine.trace_provider.TraceProvider) trace provider
        """

        self.perf_tool = get_perf_tool_instance()
        self.context = context
        self.artifact = artifact
        self.trace_provider = trace_provider
        self.response_tokens = artifact.get("responseTokens")
        self.rules = artifact.get("rules")
        self.global_mbox_name = artifact.get("globalMbox", DEFAULT_GLOBAL_MBOX)
        self.client_id = config.client
        self.request = target_options.request
        self.visitor = target_options.visitor
        self.property_token = get_property_token(self.request._property)
        self.send_notification_func = config.send_notification_func
        self.telemetry_enabled = config.telemetry_enabled if config.telemetry_enabled is not None else True
        self.visitor_id = self.request.id
        rule_evaluator = RuleEvaluator(self.client_id, self.visitor_id)
        self.process_rule = rule_evaluator.process_rule
        self.dependency = has_remote_dependency(artifact, self.request)
        self.notification_provider = NotificationProvider(self.request, self.visitor, self.send_notification_func,
                                                          self.telemetry_enabled)

    def _get_decisions(self, mode, post_processors):
        """
        :param mode: ("execute"|"prefetch") request mode
        :param post_processors: (list<callable>) post-processors used to process an mbox if needed, optional
        :return: (dict) decision response
        """
        if not getattr(self.request, mode):
            return None

        request_tracer = RequestTracer(self.trace_provider, self.artifact)

        def _view_request_accumulator(_result, key):
            _result.extend(self.rules.get("views", {}).get(key, []))
            return _result

        def _handle_view_consequence(consequences, consequence):
            if not consequences.get(consequence.name):
                consequences[consequence.name] = consequence
            else:
                existing_consequence = consequences.get(consequence.name)

                if not existing_consequence.options:
                    existing_consequence.options = []
                existing_consequence.options.extend(consequence.options or [])

                if not existing_consequence.metrics:
                    existing_consequence.metrics = []
                existing_consequence.metrics.extend(consequence.metrics or [])

        def _process_view_request(request_details, additional_post_processors=None):
            """
            :param request_details (delivery_api_client.Model.request_details.RequestDetails) request details
            :param additional_post_processors: (list<callable>) additional post-processors
            :return: (list<delivery_api_client.Model.mbox_response.MboxResponse>) decision consequences for views
            """
            if not additional_post_processors:
                additional_post_processors = []

            request_tracer.trace_request(mode, RequestType.VIEW.value, request_details, self.context)

            consequences = {}

            if request_details and request_details.name:
                view_rules = self.rules.get("views", {}).get(request_details.name, [])
            else:
                view_rules = reduce(_view_request_accumulator, self.rules.get("views", {}).keys(), [])

            view_rules = filter(by_property_token(self.property_token), view_rules)

            matched_rule_keys = set()
            _post_processors = list(post_processors)
            _post_processors.extend(additional_post_processors)

            for rule in view_rules:
                rule_key = get_rule_key(rule)
                consequence = None

                if rule_key not in matched_rule_keys:
                    consequence = self.process_rule(rule, self.context, RequestType.VIEW.value, request_details,
                                                    _post_processors, request_tracer)

                if consequence:
                    matched_rule_keys.add(rule_key)
                    _handle_view_consequence(consequences, consequence)

            return sorted(consequences.values(), key=order_by_name)

        def _process_mbox_request(mbox_request, additional_post_processors=None):
            """
            :param mbox_request (delivery_api_client.Model.mbox_request.MboxRequest) mbox request
            :param additional_post_processors: (list<callable>) additional post-processors
            :return: (list<delivery_api_client.Model.mbox_response.MboxResponse>) decision consequences for mboxes
            """
            if not additional_post_processors:
                additional_post_processors = []
            is_global_mbox = mbox_request.name == self.global_mbox_name

            request_tracer.trace_request(mode, RequestType.MBOX.value, mbox_request, self.context)

            consequences = []
            mbox_rules = filter(by_property_token(self.property_token),
                                self.rules.get("mboxes", {}).get(mbox_request.name, []))

            matched_rule_keys = set()
            _post_processors = list(post_processors)
            _post_processors.extend(additional_post_processors)

            for rule in mbox_rules:
                rule_key = get_rule_key(rule)
                consequence = None

                if not is_global_mbox or (is_global_mbox and rule_key not in matched_rule_keys):
                    consequence = self.process_rule(rule, self.context, RequestType.MBOX.value, mbox_request,
                                                    _post_processors, request_tracer)

                if consequence:
                    consequences.append(consequence)
                    matched_rule_keys.add(rule_key)
                    if not is_global_mbox:
                        break

            # add a blank if no consequences
            if not is_global_mbox and len(consequences) == 0:
                fallback_consequence = MboxResponse(name=mbox_request.name,
                                                    index=mbox_request.index,
                                                    trace=request_tracer.get_trace_result())
                consequences.append(fallback_consequence)

            return consequences

        def _process_page_load_request(request_details):
            """
            :param request_details (delivery_api_client.Model.request_details.RequestDetails) request details
            :return: (delivery_api_client.Model.mbox_response.MboxResponse) decision consequences for page load
            """

            preserved = {
                "trace": None
            }

            def _preserve_trace(rule, mbox_response, request_type, request_detail, tracer):
                preserved["trace"] = mbox_response.trace
                return mbox_response

            if request_details:
                mbox_attributes = {attr: getattr(request_details, attr) for attr, val in
                                   request_details.attribute_map.items()}
                mbox_request = MboxRequest(**mbox_attributes)
            else:
                mbox_request = MboxRequest()

            mbox_request.name = self.global_mbox_name
            consequences = _process_mbox_request(mbox_request, [_preserve_trace, remove_page_load_attributes])
            options = flatten_list([consequence.options for consequence in consequences])
            mbox_response = MboxResponse(options=options, trace=preserved.get("trace"))

            def _metrics_accumulator(indexed, consequence):
                for metric in consequence.metrics or []:
                    indexed[metric.event_token] = metric
                return indexed

            indexed_metrics = reduce(_metrics_accumulator, consequences, {})

            if indexed_metrics:
                mbox_response.metrics = sorted(indexed_metrics.values(), key=order_by_event_token)

            return mbox_response

        response = PrefetchResponse() if mode == "prefetch" else ExecuteResponse()

        if getattr(self.request, mode).mboxes:
            mboxes = getattr(self.request, mode).mboxes
            response.mboxes = flatten_list([_process_mbox_request(mbox_request) for mbox_request
                                            in mboxes if mbox_request])

        if getattr(getattr(self.request, mode), "views", None):
            views = getattr(getattr(self.request, mode), "views")
            response.views = flatten_list([_process_view_request(request_details) for request_details in views])

        page_load = getattr(self.request, mode).page_load
        response.page_load = _process_page_load_request(page_load)

        return response

    def _prepare_notification(self, rule, mbox_response, request_type, request_detail, tracer):
        """
        :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
        :param mbox_response: (delivery_api_client.Model.mbox_response.MboxResponse) mbox response
        :param request_type: ( "mbox"|"view"|"pageLoad") request type
        :param request_detail: (delivery_api_client.Model.request_details.RequestDetails) request details
        :param tracer: (target_decisioning_engine.trace_provider.RequestTracer) request tracer
        :return: (delivery_api_client.Model.mbox_response.MboxResponse)
        """
        self.notification_provider.add_notification(mbox_response, tracer.trace_notification(rule))
        return mbox_response

    def _get_execute_decisions(self, post_processors=None):
        """
        :param post_processors: (list<callable>) post-processors used to process an mbox if needed, optional
        :return: (dict) execute decision response
        """
        if not post_processors:
            post_processors = []
        all_post_processors = [self._prepare_notification, prepare_execute_response]
        all_post_processors.extend(post_processors)
        return self._get_decisions("execute", all_post_processors)

    def _get_prefetch_decisions(self, post_processors=None):
        """
        :param post_processors: (list<callable>) post-processors used to process an mbox if needed, optional
        :return: (dict) prefetch decision response
        """
        if not post_processors:
            post_processors = []
        all_post_processors = [prepare_prefetch_response]
        all_post_processors.extend(post_processors)
        return self._get_decisions("prefetch", all_post_processors)

    def run(self):
        """Public function for executing decisioning logic
        :return: (target_decisioning_engine.types.decision_provider_response.DecisionProviderResponse)
        """
        self.perf_tool.time_start(TIMING_GET_OFFER)
        add_response_tokens = create_response_tokens_post_processor(self.context, self.response_tokens)
        common_post_processor = [add_response_tokens, replace_campaign_macros, add_trace]
        response = DecisionProviderResponse(
            status=PARTIAL_CONTENT if self.dependency.get("remote_needed") is True else OK,
            remote_mboxes=self.dependency.get("remote_mboxes"),
            remote_views=self.dependency.get("remote_views"),
            request_id=self.request.request_id,
            _id=self.request.id,
            client=self.client_id,
            execute=self._get_execute_decisions(common_post_processor),
            prefetch=self._get_prefetch_decisions(common_post_processor)
        )

        telemetry_entry = TelemetryEntry(execution=self.perf_tool.time_end(TIMING_GET_OFFER))
        self.notification_provider.add_telemetry_entry(telemetry_entry)
        self.notification_provider.send_notifications()
        logger.debug("{} - REQUEST: {} /n RESPONSE: {}".format(LOG_TAG, self.request, response))
        return response
