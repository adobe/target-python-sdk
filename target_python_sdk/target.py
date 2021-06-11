# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Transforms user input into Delivery API request"""
# pylint: disable=protected-access
import json
from functools import partial

from target_python_sdk.messages import MESSAGES
from target_python_sdk.cookies import parse_cookies
from target_python_sdk.helper import create_delivery_api
from target_python_sdk.helper import get_device_id
from target_python_sdk.helper import get_cluster
from target_python_sdk.helper import get_target_host
from target_python_sdk.helper import get_session_id
from target_python_sdk.helper import create_headers
from target_python_sdk.helper import create_request
from target_python_sdk.helper import create_configuration
from target_python_sdk.helper import process_response
from target_python_sdk.helper import preserve_location_hint
from target_tools.logger import get_logger
from target_tools.utils import requires_decisioning_engine
from target_tools.utils import decisioning_engine_ready
from target_tools.utils import get_property
from target_tools.utils import compose_functions
from target_tools.messages import DECISIONING_ENGINE_NOT_READY
from target_tools.enums import DecisioningMethod


logger = get_logger()


def _get_request_options(options, opts_config, device_id):
    """Create Delivery API request options"""
    return {
        "logger": logger,
        "visitor": options.get("visitor"),
        "device_id": device_id,
        "consumer_id": options.get("consumer_id"),
        "environment_id": opts_config.get("environment_id"),
        "organization_id": opts_config.get("organization_id")
    }


def _create_request_context(options, opts_config, target_location_hint):
    """Create a context object for building the Delivery API request"""
    cookies = parse_cookies(options.get("target_cookie"))
    device_id = get_device_id(cookies)
    cluster = get_cluster(device_id, target_location_hint)
    host = get_target_host(opts_config.get("server_domain"), cluster,
                           opts_config.get("client"), opts_config.get("secure"))
    session_id = get_session_id(cookies, options.get("session_id"))
    headers = create_headers()
    request_options = _get_request_options(options, opts_config, device_id)
    configuration = create_configuration(host)
    return {
        "cookies": cookies,
        "device_id": device_id,
        "cluster": cluster,
        "host": host,
        "session_id": session_id,
        "headers": headers,
        "request_options": request_options,
        "configuration": configuration
    }


def execute_delivery(client_config, options, decisioning_engine=None):
    """Construct Delivery API request and send"""
    opts_config = options.get("config")
    _property = get_property(opts_config, options.get("request"))
    if _property:
        options["request"]._property = _property

    target_location_hint = options.get("target_location_hint") or opts_config.get("target_location_hint")

    if requires_decisioning_engine(opts_config.get("decisioning_method")) and \
            not decisioning_engine_ready(decisioning_engine):
        # fulfill the request remotely if hybrid execution mode and decisioning engine is unavailable
        if opts_config.get("decisioning_method") == DecisioningMethod.HYBRID.value:
            opts_config["decisioning_method"] = DecisioningMethod.SERVER_SIDE.value
        else:
            raise Exception(DECISIONING_ENGINE_NOT_READY)

    request_context = _create_request_context(options, opts_config, target_location_hint)

    delivery_request = create_request(options.get("request"), request_context.get("request_options"))

    delivery_method = create_delivery_api(
        request_context.get("configuration"),
        options.get("visitor"),
        opts_config.get("decisioning_method"),
        target_location_hint=target_location_hint,
        delivery_request=delivery_request,
        decisioning_engine=decisioning_engine
    )

    logger.debug(
        MESSAGES.get("REQUEST_SENT"),
        opts_config.get("decisioning_method"),
        request_context.get("host"),
        json.dumps(delivery_request.to_dict())
    )

    wrapped_callback = None
    if options.get("callback"):
        bound_handle_delivery_response = partial(handle_delivery_response, delivery_request, options.get("visitor"),
                                                 request_context.get("session_id"), request_context.get("cluster"),
                                                 opts_config.get("decisioning_method"), decisioning_engine)
        bound_preserve_location_hint = partial(preserve_location_hint, client_config)
        inner_callback = compose_functions(bound_preserve_location_hint, bound_handle_delivery_response)
        wrapped_callback = compose_functions(options.get("callback"), inner_callback)

    response = delivery_method.execute(
        opts_config.get("organization_id"),
        request_context.get("session_id"),
        delivery_request,
        _request_timeout=opts_config.get("timeout"),
        version=opts_config.get("version"),
        headers=request_context.get("headers"),
        async_req=bool(options.get("callback")),
        callback=wrapped_callback,
        err_callback=options.get("err_callback")
    )

    if options.get("callback"):
        return response  # returns AsyncResult to user in case they don"t want to use callback

    response_dict = handle_delivery_response(delivery_request, options.get("visitor"),
                                             request_context.get("session_id"), request_context.get("cluster"),
                                             opts_config.get("decisioning_method"), decisioning_engine, response)
    return preserve_location_hint(client_config, response_dict)


def handle_delivery_response(delivery_request, visitor, session_id,
                             cluster, decisioning_method, decisioning_engine, response):
    """Delivery API response transformer"""
    logger.debug(
        MESSAGES.get("RESPONSE_RECEIVED"),
        json.dumps(response.to_dict())
    )

    result = dict({
        "visitor_state": visitor.get_state() if visitor else None,
        "request": delivery_request
    })

    result.update(process_response(
        session_id,
        cluster,
        delivery_request,
        response,
        decisioning_method,
        decisioning_engine
    ))
    return result
