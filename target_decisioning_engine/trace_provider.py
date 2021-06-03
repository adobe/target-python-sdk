# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""TraceProvider, RequestTracer, and ArtifactTracer classes"""
import datetime
from copy import deepcopy

from target_decisioning_engine.messages import MESSAGES
from target_decisioning_engine.constants import ACTIVITY_TYPE
from target_decisioning_engine.constants import ACTIVITY_ID
from target_decisioning_engine.constants import OFFER_ID
from target_decisioning_engine.constants import EXPERIENCE_ID
from target_decisioning_engine.constants import AUDIENCE_IDS
from target_decisioning_engine.types.decisioning_artifact import DecisioningArtifactMeta
from target_tools.utils import is_string
from target_tools.utils import to_dict


def by_order(item):
    """
    :param item: (dict) item from list being sorted
    :return: (int) Returns numeric order value
    """
    return item.get("order")


class TraceProvider:
    """TraceProvider"""

    def __init__(self, config, target_options, artifact_trace):
        """
        :param config: (target_decisioning_engine.types.decisioning_config.DecisioningConfig) config
        :param target_options: (target_decisioning_engine.types.target_delivery_request.TargetDeliveryRequest) options
        :param artifact_trace: (dict) artifact trace
        """
        self.config = config
        self.target_options = target_options
        self.artifact_trace = artifact_trace
        self.client_code = config.client
        self.session_id = target_options.session_id
        self.request = target_options.request
        self.show_traces = self.request.trace is not None
        self.profile = None

        tnt_id_parts = self.request.id.tnt_id.split(".") if self.request.id and is_string(self.request.id.tnt_id) \
            else [None, None]
        tnt_id = tnt_id_parts[0]
        profile_location = tnt_id_parts[1] if len(tnt_id_parts) >= 2 else None

        visitor_id = to_dict(self.request.id)
        visitor_id["tntId"] = tnt_id
        visitor_id["profileLocation"] = profile_location
        self.profile = {
            "visitorId": visitor_id
        }

    def wrap(self, trace_result):
        """
        :param trace_result: (dict) trace data
        :return: (dict) Returns wrapper object with complete trace
        """
        if not self.show_traces:
            return None

        trace_request = deepcopy(trace_result.get("request"))
        _request = {
            "sessionId": self.session_id
        }
        _request.update(trace_request)
        return {
            "clientCode": self.client_code,
            "artifact": self.artifact_trace,
            "profile": self.profile,
            "request": _request,
            "campaigns": trace_result.get("campaigns"),
            "evaluatedCampaignTargets": trace_result.get("evaluatedCampaignTargets")
        }


class RequestTracer:
    """RequestTracer"""

    def __init__(self, trace_provider, artifact):
        """
        :param trace_provider: (target_decisioning_engine.trace_provider.TraceProvider) trace provider
        :param artifact: (target_decisioning_engine.types.decisioning_artifact.DecisioningArtifact) artifact
        """
        self.trace_provider = trace_provider
        self.artifact = artifact
        self.request = {}
        self.campaigns = {}
        self.campaign_order = 0
        self.evaluated_campaign_targets = {}
        self.evaluated_campaign_target_order = 0

    def trace_request(self, mode, request_type, mbox_request, context):
        """Sets request details on self.request
        :param mode: ("execute"|"prefetch") mode
        :param request_type: ("mbox"|"view"|"pageLoad") request type
        :param mbox_request: (delivery_api_client.Model.request_details.RequestDetails|
            delivery_api_client.Model.mbox_request.MboxRequest) request details
        :param context: (target_decisioning_engine.types.decisioning_context.DecisioningContext) decisioning context
        """
        self.request = {"pageURL": context.get("page", {}).get("url"),
                        "host": context.get("page", {}).get("domain"),
                        request_type: to_dict(mbox_request) if mbox_request else {}}
        self.request[request_type]["type"] = mode

    def _add_campaign(self, rule, rule_satisfied):
        """Sets details on self.campaigns and increments self.campaign_order
        :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) decisioning rule
        :param rule_satisfied: (bool) is rule satisfied
        """
        meta = rule.get("meta")
        activity_id = meta.get(ACTIVITY_ID)

        if rule_satisfied and not self.campaigns.get(activity_id):
            self.campaign_order += 1
            self.campaigns[activity_id] = {
                "id": activity_id,
                "order": self.campaign_order,
                "campaignType": meta.get(ACTIVITY_TYPE),
                "branchId": meta.get(EXPERIENCE_ID),
                "offers": [meta.get(OFFER_ID)] if meta.get(OFFER_ID) else [],
                "environment": self.artifact.get("meta", {}).get("environment")
            }

    def _add_evaluated_campaign_target(self, rule, rule_context, rule_satisfied):
        """Sets details on self.evaluated_campaign_targets and increments self.evaluated_campaign_target_order
        :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) decisioning rule
        :param rule_context: (target_decisioning_engine.types.decisioning_context.DecisioningContext) context
        :param rule_satisfied: (bool) is rule satisfied
        """
        meta = rule.get("meta")
        audience_ids = meta.get(AUDIENCE_IDS)
        activity_id = meta.get(ACTIVITY_ID)

        if not self.evaluated_campaign_targets.get(activity_id):
            self.evaluated_campaign_target_order += 1

            self.evaluated_campaign_targets[activity_id] = {
                "order": self.evaluated_campaign_target_order,
                "context": rule_context,
                "campaignId": activity_id,
                "campaignType": meta.get(ACTIVITY_TYPE),
                "matchedSegmentIds": set(),
                "unmatchedSegmentIds": set(),
                "matchedRuleConditions": [],
                "unmatchedRuleConditions": []
            }

        segment_ids_key = "matchedSegmentIds" if rule_satisfied else "unmatchedSegmentIds"
        for audience_id in audience_ids:
            self.evaluated_campaign_targets[activity_id][segment_ids_key].add(audience_id)

        rule_conditions_key = "matchedRuleConditions" if rule_satisfied else "unmatchedRuleConditions"
        self.evaluated_campaign_targets[activity_id][rule_conditions_key].append(rule.get("condition"))

    def trace_rule_evaluated(self, rule, rule_context, rule_satisfied):
        """
        :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) decisioning rule
        :param rule_context: (target_decisioning_engine.types.decisioning_context.DecisioningContext) context
        :param rule_satisfied: (bool) is rule satisfied
        """
        self._add_campaign(rule, rule_satisfied)
        self._add_evaluated_campaign_target(rule, rule_context, rule_satisfied)

    def trace_notification(self, rule):
        """
        :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) decisioning rule
        :return: (callable) Returns function that appends notification to campaigns object
        """
        meta = rule.get("meta")
        activity_id = meta.get(ACTIVITY_ID)

        if self.campaigns.get(activity_id) and not self.campaigns.get(activity_id).get("notifications"):
            self.campaigns[activity_id]["notifications"] = []

        def append_notification(notification):
            """
            :param notification: (dict) notification
            """
            self.campaigns[activity_id]["notifications"].append(notification)

        return append_notification

    def to_dict(self):
        """
        :return: (dict) returns request trace data as a dict
        """
        sorted_campaigns = deepcopy(sorted(list(self.campaigns.values()), key=by_order))
        for campaign in sorted_campaigns:
            campaign.pop("order", None)

        campaign_targets = deepcopy(sorted(list(self.evaluated_campaign_targets.values()), key=by_order))
        for campaign_target in campaign_targets:
            campaign_target["matchedSegmentIds"] = sorted(list(campaign_target.get("matchedSegmentIds")))
            campaign_target["unmatchedSegmentIds"] = sorted(list(campaign_target.get("unmatchedSegmentIds")))
            campaign_target.pop("order", None)

        return {
            "campaigns": sorted_campaigns,
            "evaluatedCampaignTargets": campaign_targets,
            "request": self.request
        }

    def get_trace_result(self):
        """
        :return: (dict) Returns trace data
        """
        return self.trace_provider.wrap(self.to_dict())


class ArtifactTracer:
    """ArtifactTracer"""

    def __init__(self, artifact_location, artifact_payload, polling_interval, polling_halted, first_artifact):
        """
        :param artifact_location: (str) artifact location
        :param artifact_payload: (target_decisioning_engine.types.decisioning_artifact.DecisioningArtifact) artifact
        :param polling_interval: (int) polling interval
        :param polling_halted: (bool) is polling currently paused
        :param first_artifact: (target_decisioning_engine.types.decisioning_artifact.DecisioningArtifact) first artifact
        """
        self.artifact_location = artifact_location
        self.artifact_payload = artifact_payload
        self.polling_interval = polling_interval
        self.polling_halted = polling_halted
        self.artifact = first_artifact
        self.artifact_retrieval_count = 1
        self.artifact_last_retrieved = datetime.datetime.utcnow()
        self.meta = self.artifact.get("meta") if self.artifact else DecisioningArtifactMeta()

    def provide_new_artifact(self, artifact):
        """
        :param artifact: (target_decisioning_engine.types.decisioning_artifact.DecisioningArtifact) artifact
        """
        self.artifact_last_retrieved = datetime.datetime.utcnow()
        self.artifact_retrieval_count += 1
        self.artifact = artifact

    def to_dict(self):
        """
        :return: (dict) returns artifact trace data as a dict
        """
        trace = {
            "artifactLocation": MESSAGES.get("NOT_APPLICABLE") if self.artifact_payload else self.artifact_location,
            "pollingInterval": self.polling_interval,
            "pollingHalted": self.polling_halted,
            "artifactVersion": self.artifact.get("version") if self.artifact else MESSAGES.get("UNKNOWN"),
            "artifactRetrievalCount": self.artifact_retrieval_count,
            "artifactLastRetrieved": self.artifact_last_retrieved.isoformat()
        }
        trace.update(self.meta)
        return trace
