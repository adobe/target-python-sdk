# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""rule evaluator"""
from copy import deepcopy
from json_logic import jsonLogic
from target_decisioning_engine.allocation_provider import compute_allocation
from target_decisioning_engine.constants import ACTIVITY_ID
from target_decisioning_engine.context_provider import create_page_context
from target_decisioning_engine.context_provider import create_mbox_context
from target_tools.response_helpers import create_mbox_response
from target_tools.utils import to_dict


class RuleEvaluator:
    """RuleEvaluator"""

    def __init__(self, client_id, visitor_id):
        """
        :param client_id: (str) client ID
        :param visitor_id: (delivery_api_client.Model.visitor_id.VisitorId) visitor ID
        """
        self.client_id = client_id
        self.visitor_id = visitor_id

    def process_rule(self, rule, context, request_type, request_detail, post_processors, tracer):
        """Uses json logic to evaluate request context against the rules and returns an MboxResponse
        :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
        :param context: (target_decisioning_engine.types.decisioning_context.DecisioningContext) context
        :param request_type: ( "mbox"|"view"|"pageLoad") request type
        :param request_detail: (delivery_api_client.Model.request_details.RequestDetails |
            delivery_api_client.Model.mbox_request.MboxRequest) request details
        :param post_processors: (list<callable>) post-processors used to process an mbox if needed
        :param tracer: (target_decisioning_engine.trace_provider.RequestTracer) request tracer
        :return: (delivery_api_client.Model.mbox_response.MboxResponse)
        """
        rule_context = deepcopy(context)
        consequence = None
        page = rule_context.get("page")
        referring = rule_context.get("referring")

        if request_detail and request_detail.address:
            page = create_page_context(request_detail.address) or page
            referring = create_page_context(request_detail.address) or referring

        rule_context.update({
            "page": to_dict(page),
            "referring": to_dict(referring),
            "mbox": to_dict(create_mbox_context(request_detail)),
            "allocation": compute_allocation(self.client_id, rule.get("meta", {}).get(ACTIVITY_ID), self.visitor_id)
        })

        rule_satisfied = jsonLogic(rule.get("condition"), rule_context)
        tracer.trace_rule_evaluated(rule, rule_context, rule_satisfied)

        if rule_satisfied:
            consequence = create_mbox_response(deepcopy(rule.get("consequence")))
            consequence.index = request_detail.index if hasattr(request_detail, "index") else None

            for post_process_func in post_processors:
                consequence = post_process_func(rule, consequence, request_type, request_detail, tracer)
        return consequence
