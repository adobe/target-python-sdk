# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Post-processing functions for DecisionProvider"""
try:
    from functools import reduce
except ImportError:
    pass
import re
from copy import deepcopy
from delivery_api_client import MetricType
from delivery_api_client import OptionType
import target_decisioning_engine.constants as DecisioningConstants
from target_decisioning_engine.enums import RequestType
from target_tools.utils import is_string
from target_tools.utils import get_value_from_object
from target_tools.response_helpers import create_action



MACRO_PATTERN_REGEX = r"\${([a-zA-Z0-9_.]*?)}"

MACRO_NAME_REPLACEMENTS = {
    "campaign": "activity",
    "recipe": "experience"
}

RESPONSE_TOKEN_KEYS = [
    DecisioningConstants.ACTIVITY_ID,
    DecisioningConstants.ACTIVITY_NAME,
    DecisioningConstants.ACTIVITY_TYPE,
    DecisioningConstants.EXPERIENCE_ID,
    DecisioningConstants.EXPERIENCE_NAME,
    DecisioningConstants.LOCATION_ID,
    DecisioningConstants.LOCATION_NAME,
    DecisioningConstants.LOCATION_TYPE,
    DecisioningConstants.OFFER_ID,
    DecisioningConstants.OFFER_NAME,
    DecisioningConstants.OPTION_ID,
    DecisioningConstants.OPTION_NAME
]

MACRO_NAME_REPLACEMENTS_REGEX = r"{}".format("|".join(MACRO_NAME_REPLACEMENTS.keys()))

MACRO_NAME_REMOVALS = ["mbox"]


def no_blank_options(_option):
    """
    :param _option: (delivery_api_client.Model.option.Option)
    :return: (bool) True if option contains type and content, False otherwise
    """
    return _option.type and _option.content


def update_execute_option(_option):
    """
    :param _option: (delivery_api_client.Model.option.Option)
    :return: transformed option
    """
    _option.event_token = None
    return _option


def prepare_execute_response(rule, mbox_response, request_type, request_detail, tracer):
    """
    :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
    :param mbox_response: (delivery_api_client.Model.mbox_response.MboxResponse) mbox response
    :param request_type: ( "mbox"|"view"|"pageLoad") request type
    :param request_detail: (delivery_api_client.Model.request_details.RequestDetails) request details
    :param tracer: (target_decisioning_engine.trace_provider.RequestTracer) request tracer
    :return: (delivery_api_client.Model.mbox_response.MboxResponse)
        Returns mbox response with updated options and metrics
    """
    metrics = mbox_response.metrics or []
    options = mbox_response.options or []

    result = deepcopy(mbox_response)
    result.options = \
        [update_execute_option(pristine_option) for pristine_option in options if no_blank_options(pristine_option)]

    filtered_metrics = [metric for metric in metrics if metric.type == MetricType.CLICK]
    if filtered_metrics:
        result.metrics = filtered_metrics

    return result


def update_prefetch_option(mbox_response, _option, index):
    """
    :param mbox_response: (delivery_api_client.Model.mbox_response.MboxResponse) mbox response
    :param _option: (delivery_api_client.Model.option.Option)
    :param index: (int) index of _option in mbox_response.options list
    :return: transformed option
    """
    event_token = _option.event_token
    if not event_token and len(mbox_response.metrics) > index \
            and mbox_response.metrics[index].type == MetricType.DISPLAY:
        event_token = mbox_response.metrics[index].event_token

    _option.event_token = event_token
    return _option


def prepare_prefetch_response(rule, mbox_response, request_type, request_detail, tracer):
    """
    :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
    :param mbox_response: (delivery_api_client.Model.mbox_response.MboxResponse) mbox response
    :param request_type: ( "mbox"|"view"|"pageLoad") request type
    :param request_detail: (delivery_api_client.Model.request_details.RequestDetails) request details
    :param tracer: (target_decisioning_engine.trace_provider.RequestTracer) request tracer
    :return: (delivery_api_client.Model.mbox_response.MboxResponse)
        Returns mbox response with updated options and metrics
    """
    mbox_response_copy = deepcopy(mbox_response)
    options = mbox_response_copy.options or []

    mbox_response_copy.options = \
        [update_prefetch_option(mbox_response_copy, pristine_option, index) for index, pristine_option
         in enumerate(options)]

    if request_type != RequestType.VIEW.value:
        mbox_response_copy.metrics = None

    return mbox_response_copy


def add_trace(rule, mbox_response, request_type, request_detail, tracer):
    """
    :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
    :param mbox_response: (delivery_api_client.Model.mbox_response.MboxResponse) mbox response
    :param request_type: ( "mbox"|"view"|"pageLoad") request type
    :param request_detail: (delivery_api_client.Model.request_details.RequestDetails) request details
    :param tracer: (target_decisioning_engine.trace_provider.RequestTracer) request tracer
    :return: (delivery_api_client.Model.mbox_response.MboxResponse)
        Returns mbox response with updated options and metrics
    """
    result = deepcopy(mbox_response)
    result.trace = tracer.get_trace_result()
    return result


def remove_page_load_attributes(rule, mbox_response, request_type, request_detail, tracer):
    """
    :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
    :param mbox_response: (delivery_api_client.Model.mbox_response.MboxResponse) mbox response
    :param request_type: ( "mbox"|"view"|"pageLoad") request type
    :param request_detail: (delivery_api_client.Model.request_details.RequestDetails) request details
    :param tracer: (target_decisioning_engine.trace_provider.RequestTracer) request tracer
    :return: (delivery_api_client.Model.mbox_response.MboxResponse)
        Returns mbox response with updated options and metrics
    """
    processed = deepcopy(mbox_response)
    processed.index = None
    processed.name = None
    processed.trace = None
    return processed


def add_response_tokens_to_option(_option, response_tokens, response_tokens_from_meta):
    """
    :param _option: (delivery_api_client.Model.option.Option) response option
    :param response_tokens: (list<str>) list of response tokens from decisioning context
    :param response_tokens_from_meta: (list<str>) list of response tokens from decisioning rule meta
    :return: (delivery_api_client.Model.option.Option) Returns option updated with response tokens
    """
    _option.response_tokens = dict(response_tokens_from_meta)
    _option.response_tokens.update(response_tokens)
    return _option


def create_response_tokens_post_processor(context, response_tokens_in_artifact=None):
    """
    :param context: (target_decisioning_engine.types.decisioning_context.DecisioningContext) decisioning context
    :param response_tokens_in_artifact: (list<str>) list of response tokens in decision artifact
    :return: (callable) Returns function that adds response tokens to mbox response
    """
    if not response_tokens_in_artifact:
        response_tokens_in_artifact = []

    response_tokens = {
        DecisioningConstants.ACTIVITY_DECISIONING_METHOD: "on-device"
    }

    geo = context.get("geo", {})
    if DecisioningConstants.GEO_CITY in response_tokens_in_artifact and geo.get("city"):
        response_tokens[DecisioningConstants.GEO_CITY] = geo.get("city")

    if DecisioningConstants.GEO_COUNTRY in response_tokens_in_artifact and geo.get("country"):
        response_tokens[DecisioningConstants.GEO_COUNTRY] = geo.get("country")

    if DecisioningConstants.GEO_STATE in response_tokens_in_artifact and geo.get("region"):
        response_tokens[DecisioningConstants.GEO_STATE] = geo.get("region")

    if DecisioningConstants.GEO_LATITUDE in response_tokens_in_artifact and geo.get("latitude"):
        response_tokens[DecisioningConstants.GEO_LATITUDE] = geo.get("latitude")

    if DecisioningConstants.GEO_LONGITUDE in response_tokens_in_artifact and geo.get("longitude"):
        response_tokens[DecisioningConstants.GEO_LONGITUDE] = geo.get("longitude")

    def add_response_tokens(rule, mbox_response, request_type, request_detail, tracer):
        """
        :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
        :param mbox_response: (delivery_api_client.Model.mbox_response.MboxResponse) mbox response
        :param request_type: ( "mbox"|"view"|"pageLoad") request type
        :param request_detail: (delivery_api_client.Model.request_details.RequestDetails) request details
        :param tracer: (target_decisioning_engine.trace_provider.RequestTracer) request tracer
        :return: (delivery_api_client.Model.mbox_response.MboxResponse) mbox response
        """
        mbox_response_copy = deepcopy(mbox_response)
        meta = rule.get("meta", {})

        def response_token_accumulator(result, response_token_key):
            """Used in reduce fn to gather response tokens"""
            if response_token_key in response_tokens_in_artifact and response_token_key in meta:
                result[response_token_key] = meta[response_token_key]

            return result

        response_tokens_from_meta = reduce(response_token_accumulator, RESPONSE_TOKEN_KEYS, {})
        options = [add_response_tokens_to_option(option, response_tokens, response_tokens_from_meta)
                   for option in mbox_response_copy.options]

        mbox_response_copy.options = options
        return mbox_response_copy

    return add_response_tokens


def add_campaign_macro_values(html_content, rule, request_detail):
    """
    :param html_content: (str) html offer content
    :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
    :param request_detail: (delivery_api_client.Model.request_details.RequestDetails) request details
    :return: (str) Returns html content with updated campaign content
    """
    if not html_content or not is_string(html_content):
        return html_content

    def replace_match(match):
        """
        :param match: (MatchObject) match found by regex pattern
        :return: (str) Returns replacement string
        """

        def replace_group_match(group_match):
            """
            :param group_match: (MatchObject) match found by regex pattern
            :return: (str) Returns replacement string
            """
            return MACRO_NAME_REPLACEMENTS[group_match.group(0)]

        if not match or not len(match.groups()) > 0:
            return match.group(0)  # entire match

        macro_key = match.group(1)
        parts = re.sub(MACRO_NAME_REPLACEMENTS_REGEX, replace_group_match, macro_key, flags=re.IGNORECASE).split(".")
        if len(parts) > 2:
            parts = parts[len(parts) - 2:]
        filtered = [part for part in parts if part not in MACRO_NAME_REMOVALS]
        key = ".".join(filtered)
        parameters = request_detail.parameters if request_detail and request_detail.parameters else {}
        for item in [rule.get("meta"), request_detail, parameters]:
            replacement = get_value_from_object(item, key)
            if replacement is not None:
                return str(replacement)
        return match.group(0)

    return re.sub(MACRO_PATTERN_REGEX, replace_match, html_content, flags=re.IGNORECASE)


def update_action_campaign_content(action, rule, request_detail):
    """
    :param action: (delivery_api_client.Model.action.Action) offer action
    :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
    :param request_detail: (delivery_api_client.Model.request_details.RequestDetails) request details
    :return: (delivery_api_client.Model.action.Action) Returns action with updated campaign content
    """
    action.content = add_campaign_macro_values(action.content, rule, request_detail)
    return action


def update_option_campaign_content(_option, rule, request_detail):
    """
    :param _option: (delivery_api_client.Model.option.Option) response option
    :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
    :param request_detail: (delivery_api_client.Model.request_details.RequestDetails) request details
    :return:  (delivery_api_client.Model.option.Option) Returns option with updated campaign content
    """
    if _option.type == OptionType.HTML:
        _option.content = add_campaign_macro_values(_option.content, rule, request_detail)
    if _option.type == OptionType.ACTIONS:
        _option.content = [update_action_campaign_content(create_action(action), rule, request_detail) for action in
                           _option.content]
    return _option


def replace_campaign_macros(rule, mbox_response, request_type, request_detail, tracer):
    """
    :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
    :param mbox_response: (delivery_api_client.Model.mbox_response.MboxResponse) mbox response
    :param request_type: ( "mbox"|"view"|"pageLoad") request type
    :param request_detail: (delivery_api_client.Model.request_details.RequestDetails) request details
    :param tracer: (target_decisioning_engine.trace_provider.RequestTracer) request tracer
    :return: (delivery_api_client.Model.mbox_response.MboxResponse)
        Returns mbox response with updated options and metrics
    """

    mbox_response_copy = deepcopy(mbox_response)
    mbox_response_copy.options = [update_option_campaign_content(option, rule, request_detail)
                                  for option in mbox_response_copy.options]
    return mbox_response_copy
