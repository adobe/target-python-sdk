# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Helper functions for building out DeliveryResponse"""
from delivery_api_client import Action
from delivery_api_client import MboxResponse
from delivery_api_client import AnalyticsResponse
from delivery_api_client import AnalyticsPayload
from delivery_api_client import Metric
from delivery_api_client import Option


def create_options(mbox):
    """Create list of Option objects"""
    if not mbox:
        return None

    result_options = []
    if mbox.get("options"):
        for _option in mbox.get("options"):
            option = Option(type=_option.get("type"),
                            content=_option.get("content"),
                            event_token=_option.get("eventToken"),
                            response_tokens=_option.get("responseTokens"))
            result_options.append(option)

    return result_options


def create_metrics(mbox):
    """Create list of Metric objects"""
    if not mbox:
        return None

    result_metrics = []
    if mbox.get("metrics"):
        for _metric in mbox.get("metrics"):
            metric = Metric(type=_metric.get("type"),
                            selector=_metric.get("selector"),
                            event_token=_metric.get("eventToken"))
            result_metrics.append(metric)

    return result_metrics


def create_analytics_response(mbox):
    """Create AnalyticsResponse"""
    if not mbox:
        return None

    _analytics = mbox.get("analytics")
    if _analytics:
        _payload = _analytics.get("payload")
        if not _payload:
            return None
        payload = AnalyticsPayload(**_payload)
        return AnalyticsResponse(payload=payload)

    return None


def create_mbox_response(consequence):
    """Convert mbox response dict to MboxResponse instance
    :param consequence: (dict) decision consequence in form of an mbox response
    :return: (delivery_api_client.Model.mbox_response.MboxResponse) mbox response
    """
    return MboxResponse(index=consequence.get("index"),
                        name=consequence.get("name"),
                        options=create_options(consequence),
                        metrics=create_metrics(consequence),
                        analytics=create_analytics_response(consequence))


def create_action(_action):
    """Create Action"""
    if not _action:
        return None

    return Action(type=_action.get("type"),
                  content=_action.get("content"),
                  selector=_action.get("selector"),
                  css_selector=_action.get("cssSelector"))
