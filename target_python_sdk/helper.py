# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Helper functions for sending requests to Delivery API"""
try:
    from functools import reduce
except ImportError:
    pass
from copy import deepcopy
import pkg_resources
from delivery_api_client import ApiClient
from delivery_api_client import MobilePlatformType
from delivery_api_client import DeviceType
from delivery_api_client import ScreenOrientationType
from delivery_api_client import ExecuteResponse
from delivery_api_client import PrefetchResponse
from delivery_api_client import CustomerId
from delivery_api_client import MetricType
from delivery_api_client import Configuration
from delivery_api_client import AnalyticsRequest
from delivery_api_client import AudienceManager
from delivery_api_client import AuthenticatedState
from delivery_api_client import ChannelType
from delivery_api_client import Context
from delivery_api_client import ExperienceCloud
from delivery_api_client import LoggingType
from delivery_api_client import VisitorId
from delivery_api_client import DeliveryApi
from target_python_sdk import MESSAGES
from target_python_sdk.cookies import DEVICE_ID_COOKIE
from target_python_sdk.cookies import SESSION_ID_COOKIE
from target_python_sdk.cookies import LOCATION_HINT_COOKIE
from target_python_sdk.cookies import create_target_cookie
from target_python_sdk.local_delivery_api import LocalDeliveryApi
from target_python_sdk.types.target_delivery_response import TargetDeliveryResponse
from target_tools.utils import is_string
from target_tools.utils import parse_int
from target_tools.utils import create_uuid
from target_tools.utils import is_dict
from target_tools.utils import is_int
from target_tools.utils import get_timezone_offset
from target_tools.utils import get_epoch_time
from target_tools.utils import flatten_list
from target_tools.utils import remove_empty_values
from target_tools.utils import requires_decisioning_engine
from target_tools.constants import DEFAULT_GLOBAL_MBOX
from target_tools.constants import EMPTY_REQUEST
from target_tools.logger import get_logger
from target_tools.enums import DecisioningMethod

SDK_VERSION = pkg_resources.require("target_python_sdk")[0].version

SCHEME = {
    "HTTP": "http://",
    "HTTPS": "https://"
}

AUTH_STATE = {
    "0": AuthenticatedState.UNKNOWN,
    "1": AuthenticatedState.AUTHENTICATED,
    "2": AuthenticatedState.LOGGED_OUT
}

EDGE_CLUSTER_PREFIX = "mboxedge"
HOST = "tt.omtrdc.net"
SESSION_ID_MAX_AGE = 1860
DEVICE_ID_MAX_AGE = 63244800
LOCATION_HINT_MAX_AGE = 1860

CHANNEL_TYPES = [ChannelType.WEB, ChannelType.MOBILE]
PLATFORM_TYPES = [MobilePlatformType.ANDROID, MobilePlatformType.IOS]
DEVICE_TYPES = [DeviceType.PHONE, DeviceType.TABLET]
SCREEN_ORIENTATION_TYPES = [ScreenOrientationType.PORTRAIT, ScreenOrientationType.LANDSCAPE]
METRIC_TYPES = [MetricType.CLICK, MetricType.DISPLAY]

logger = get_logger()


def create_headers(uuid_method=create_uuid):
    """Create request headers to send to Delivery API"""
    return {
        "Content-Type": "application/json",
        "X-EXC-SDK": "AdobeTargetPython",
        "X-EXC-SDK-Version": SDK_VERSION,
        "X-Request-Id": uuid_method()
    }


def get_session_id(cookies, user_session_id, uuid_method=create_uuid):
    """Get session ID from cookie"""
    cookie = cookies.get(SESSION_ID_COOKIE, {})
    value = cookie.get("value")

    if is_string(value):
        return value

    if user_session_id:
        return user_session_id

    return uuid_method()


def get_target_host(server_domain, cluster, client, secure):
    """Construct Target server hostname"""
    scheme_prefix = SCHEME.get("HTTP") if secure is False else SCHEME.get("HTTPS")

    if is_string(cluster):
        return "{}{}{}.{}".format(scheme_prefix, EDGE_CLUSTER_PREFIX, cluster, HOST)

    if is_string(server_domain):
        return "{}{}".format(scheme_prefix, server_domain)

    return "{}{}.{}".format(scheme_prefix, client, HOST)


def extract_cluster_from_device_id(_id):
    """Parse cluster from device ID"""
    if not _id:
        return None

    parts = _id.split(".")

    if len(parts) != 2 or not parts[1]:
        return None

    node_details = parts[1].split("_")

    if len(node_details) != 2 or not node_details[0]:
        return None

    return node_details[0]


def get_device_id(cookies):
    """Get device ID from cookie"""
    cookie = cookies.get(DEVICE_ID_COOKIE, {})
    value = cookie.get("value")
    return value


def get_cluster(device_id, cluster):
    """Attempt to get cluster"""
    extracted = extract_cluster_from_device_id(device_id)
    return extracted or cluster


def preserve_location_hint(config, response):
    """Preserve location hint in client config for subsequent requests"""
    if response and response.get("target_location_hint_cookie"):
        config["target_location_hint"] = response.get("target_location_hint_cookie").get("value")
    return response


def create_delivery_api(
        configuration,
        visitor,
        decisioning_method=DecisioningMethod.SERVER_SIDE.value,
        target_location_hint=None,
        delivery_request=None,
        decisioning_engine=None):
    """Create Delivery API, based on decisioning method"""
    api_client = ApiClient(configuration=configuration)
    if requires_decisioning_engine(decisioning_method):
        decisioning_dependency = decisioning_engine.has_remote_dependency(delivery_request)

        if decisioning_method == DecisioningMethod.HYBRID.value and decisioning_dependency.get("remote_needed"):
            return DeliveryApi(api_client=api_client)

        return LocalDeliveryApi(decisioning_engine, visitor, target_location_hint)

    return DeliveryApi(api_client=api_client)


def get_marketing_cloud_visitor_id(visitor):
    """Get Marketing Cloud visitor ID"""
    if not visitor:
        return None
    visitor_values = visitor.get_visitor_values()
    return visitor_values.get("MCMID")


def get_visitor_customer_ids(visitor):
    """Get customer IDs from visitor"""
    if not visitor:
        return None
    visitor_state = visitor.get_state()
    states = list(visitor_state.keys())
    first_organization_state = visitor_state[states[0]] if states else {}
    return first_organization_state.get("customer_ids")


def customer_ids_accumulator(result, customer_id_tuple):
    """Used in reduce fn to gather customer IDs"""
    customer_id_key = customer_id_tuple[0]
    customer_id_value = customer_id_tuple[1]

    if not customer_id_value:
        return result

    if is_dict(customer_id_value):
        item = CustomerId(
            id=customer_id_value.get("id"),
            integration_code=customer_id_key,
            authenticated_state=AUTH_STATE.get(customer_id_value.get("authState"))
        )
    else:
        item = CustomerId(
            id=customer_id_value,
            integration_code=customer_id_key,
            authenticated_state=AUTH_STATE.get("0")
        )

    result.append(item)
    return result


def get_customer_ids(customer_ids, visitor):
    """Gathers customer IDs"""
    visitor_customer_ids = get_visitor_customer_ids(visitor)
    if not visitor_customer_ids:
        return customer_ids

    converted_ids = reduce(customer_ids_accumulator, list(visitor_customer_ids.items()), [])
    if not converted_ids:
        return customer_ids

    return converted_ids + customer_ids if customer_ids else converted_ids


def create_visitor_id(visitor_id, options):
    """Creates new VisitorId"""
    if not visitor_id:
        visitor_id = VisitorId()
    if not options:
        options = {}

    device_id = options.get("device_id")
    visitor = options.get("visitor")

    if not visitor_id.tnt_id:
        visitor_id.tnt_id = device_id
    if not visitor_id.marketing_cloud_visitor_id:
        visitor_id.marketing_cloud_visitor_id = get_marketing_cloud_visitor_id(visitor)
    visitor_id.customer_ids = get_customer_ids(visitor_id.customer_ids, visitor)
    return visitor_id


def set_channel(channel):
    """Set ChannelType"""
    return channel if channel in CHANNEL_TYPES else ChannelType.WEB


def create_context(context):
    """Create Context"""
    if not context:
        context = Context()

    context.time_offset_in_minutes = get_timezone_offset()
    context.channel = set_channel(context.channel)
    return context


def get_location_hint(location_hint_string):
    """Convert location hint str to int"""
    try:
        return parse_int(location_hint_string) if location_hint_string else None
    except ValueError:
        return None


def create_audience_manager(audience_manager, options):
    """Create AudienceManager"""
    if not audience_manager:
        audience_manager = AudienceManager()

    visitor = options.get("visitor")
    visitor_values = visitor.get_visitor_values() if visitor and visitor.get_visitor_values() else {}
    location_hint = audience_manager.location_hint or get_location_hint(visitor_values.get("MCAAMLH"))
    blob = audience_manager.blob or visitor_values.get("MCAAMB")

    if not location_hint and not blob:
        return None

    audience_manager.location_hint = location_hint
    audience_manager.blob = blob
    return audience_manager


def is_current_supplemental_data_id(supplemental_data_id, visitor):
    """Checks if SDID from visitor matches the current SDID"""
    visitor_state = visitor.get_state() if visitor else {}
    states = list(visitor_state.keys())
    first_organization_state = visitor_state[states[0]] if states else {}
    return first_organization_state.get("sdid") and \
           first_organization_state.get("sdid").get("supplemental_data_id_current") == supplemental_data_id


def create_supplemental_data_id(analytics, options):
    """Retrieves up-to-date SDID"""
    visitor = options.get("visitor")
    if not visitor:
        return None

    consumer_id = options.get("consumer_id", DEFAULT_GLOBAL_MBOX)
    supplemental_data_id = analytics.supplemental_data_id

    if is_current_supplemental_data_id(supplemental_data_id, visitor):
        return supplemental_data_id

    return visitor.get_supplemental_data_id(consumer_id)


def create_analytics(analytics, options):
    """Create AnalyticsRequest"""
    if not analytics:
        analytics = AnalyticsRequest()

    if not analytics.logging:
        analytics.logging = LoggingType.SERVER_SIDE
    analytics.supplemental_data_id = create_supplemental_data_id(analytics, options)
    return analytics


def create_experience_cloud(experience_cloud, options):
    """Create ExperienceCloud"""
    if not experience_cloud:
        experience_cloud = ExperienceCloud()

    experience_cloud.analytics = create_analytics(experience_cloud.analytics, options)

    experience_cloud.audience_manager = create_audience_manager(
        experience_cloud.audience_manager,
        options
    )

    return experience_cloud


def valid_mbox(mbox):
    """Checks for valid mbox"""
    result = mbox and mbox.name
    if not result:
        logger.error("{}\n{}".format(MESSAGES.get("MBOX_INVALID"), mbox.to_str()))
    return result


def create_mboxes(mboxes):
    """Filters out invalid MboxRequest objects"""
    if not mboxes:
        return None
    valid_mboxes = [mbox for mbox in mboxes if valid_mbox(mbox)]
    return valid_mboxes or None


def valid_notification(notification):
    """Checks for valid notification"""
    is_valid = notification and is_string(notification.id) \
               and is_int(notification.timestamp) \
               and notification.type in METRIC_TYPES

    if not is_valid:
        logger.error("{}\n{}".format(MESSAGES.get("NOTIFICATION_INVALID"), notification.to_str()))

    return is_valid


def create_notifications(notifications):
    """Validate Notification objects"""
    if not notifications:
        return None

    valid_notifications = [notification for notification in notifications if valid_notification(notification)]
    return valid_notifications or None


def create_configuration(host):
    """Create new Configuration"""
    return Configuration(host=host)


def create_execute(execute):
    """Validate Execute request"""
    if not execute:
        return None

    page_load = execute.page_load
    mboxes = execute.mboxes

    if not page_load and not mboxes:
        return None

    execute.mboxes = create_mboxes(mboxes) if mboxes else None
    return execute


def create_prefetch(prefetch):
    """Validate Prefetch request"""
    if not prefetch:
        return None

    page_load = prefetch.page_load
    views = prefetch.views
    mboxes = prefetch.mboxes

    if not page_load and not views and not mboxes:
        return None

    prefetch.mboxes = create_mboxes(mboxes) if mboxes else None
    return prefetch


def create_property(_property):
    """Validate DeliveryRequest property object"""
    return _property if _property and _property.token and is_string(_property.token) else None


def create_request(incoming_request, options):
    """Update incoming DeliveryRequest"""
    uuid_method = options.get("uuid_method", create_uuid)
    delivery_request = deepcopy(incoming_request)
    delivery_request.request_id = uuid_method()
    delivery_request.environment_id = options.get("environment_id")
    delivery_request.id = create_visitor_id(incoming_request.id, options)
    delivery_request._property = create_property(incoming_request._property)
    delivery_request.trace = incoming_request.trace
    delivery_request.context = create_context(incoming_request.context)
    delivery_request.experience_cloud = create_experience_cloud(
        incoming_request.experience_cloud,
        options
    )
    delivery_request.execute = create_execute(delivery_request.execute)
    delivery_request.prefetch = create_prefetch(delivery_request.prefetch)
    delivery_request.notifications = create_notifications(delivery_request.notifications)
    return delivery_request


def get_target_cookie(session_id, _id):
    """Create Target cookie by joining several individual cookies"""
    now_in_seconds = get_epoch_time()

    cookies = []
    tnt_id = _id.tnt_id

    cookies.append({
        "name": SESSION_ID_COOKIE,
        "value": session_id,
        "expires": now_in_seconds + SESSION_ID_MAX_AGE
    })

    if tnt_id:
        cookies.append({
            "name": DEVICE_ID_COOKIE,
            "value": tnt_id,
            "expires": now_in_seconds + DEVICE_ID_MAX_AGE
        })

    return create_target_cookie(cookies)


def extract_cluster_from_edge_host(host):
    """Parse cluster from Edge hostname"""
    if not host:
        return None

    parts = host.split(".")

    if len(parts) != 4 or not parts[0]:
        return None

    return parts[0].replace(EDGE_CLUSTER_PREFIX, "")


def request_location_hint_cookie(target_client, target_location_hint):
    """Use existing target_location_hint to create cookie, otherwise make a get_offers request to get it"""
    if target_location_hint:
        return {
            "target_location_hint_cookie": get_target_location_hint_cookie(target_location_hint)
        }
    try:
        return target_client.get_offers({
            "session_id": "ping123",
            "decisioning_method": DecisioningMethod.SERVER_SIDE.value,
            "request": EMPTY_REQUEST
        })
    except Exception as err:
        logger.error("{}\n{}".format(MESSAGES.get("LOCATION_HINT_REQUEST_FAILED"), str(err)))
        return None


def get_target_location_hint_cookie(request_cluster, edge_host=None):
    """Create location hint cookie"""
    host_cluster = extract_cluster_from_edge_host(edge_host)
    cluster = request_cluster or host_cluster

    if not cluster:
        return None

    return {
        "name": LOCATION_HINT_COOKIE,
        "value": cluster,
        "maxAge": LOCATION_HINT_MAX_AGE
    }


def get_analytics_from_object(_object):
    """Get analytics response payload"""
    if not _object:
        return None

    analytics = _object.analytics
    return [analytics] if analytics else None


def get_analytics_from_list(_list):
    """Get analytics response payload from list within response"""
    if not _list:
        return None
    return flatten_list([get_analytics_from_object(item) for item in _list if item and item.analytics])


def get_analytics_details(response):
    """Get all analytics payloads from all parts of the response"""
    execute = response.execute or ExecuteResponse()
    prefetch = response.prefetch or PrefetchResponse()

    if not execute and not prefetch:
        return None

    execute_page_load_analytics = get_analytics_from_object(execute.page_load)
    execute_mbox_analytics = get_analytics_from_list(execute.mboxes)
    prefetch_page_load_analytics = get_analytics_from_object(prefetch.page_load)
    prefetch_views_analytics = get_analytics_from_list(prefetch.views)
    prefetch_mbox_analytics = get_analytics_from_list(prefetch.mboxes)

    analytics = [
        execute_page_load_analytics,
        execute_mbox_analytics,
        prefetch_page_load_analytics,
        prefetch_views_analytics,
        prefetch_mbox_analytics
    ]

    result = flatten_list([item for item in analytics if item])
    return result or None


def get_trace_from_object(_object):
    """Get trace from response payload"""
    if not _object:
        return None

    trace = _object.trace
    return [trace] if trace else None


def get_trace_from_list(_list):
    """Get trace from within list in response payload"""
    if not _list:
        return None
    return flatten_list([get_trace_from_object(item) for item in _list if item and item.trace])


def get_trace_details(response):
    """Get trace details from all parts of response payload"""
    execute = response.execute or ExecuteResponse()
    prefetch = response.prefetch or PrefetchResponse()

    if not execute and not prefetch:
        return None

    execute_page_load_trace = get_trace_from_object(execute.page_load)
    execute_mbox_trace = get_trace_from_list(execute.mboxes)
    prefetch_page_load_trace = get_trace_from_object(prefetch.page_load)
    prefetch_views_trace = get_trace_from_list(prefetch.views)
    prefetch_mbox_trace = get_trace_from_list(prefetch.mboxes)

    analytics = [
        execute_page_load_trace,
        execute_mbox_trace,
        prefetch_page_load_trace,
        prefetch_views_trace,
        prefetch_mbox_trace
    ]

    result = flatten_list([item for item in analytics if item])
    return result or None


def get_response_tokens_from_object(_object):
    """Get response tokens from response payload"""
    if not _object:
        return []

    options = _object.options or []
    return [option.response_tokens for option in options if option.response_tokens]


def get_response_tokens_from_list(_list):
    """Get response tokens from list within response payload"""
    if not _list:
        return None
    return flatten_list([get_response_tokens_from_object(item) for item in _list if item])


def get_response_tokens(response):
    """Get all response tokens from all parts of response payload"""
    execute = response.execute or ExecuteResponse()
    prefetch = response.prefetch or PrefetchResponse()

    if not execute and not prefetch:
        return None

    execute_page_load_trace = get_response_tokens_from_object(execute.page_load)
    execute_mbox_trace = get_response_tokens_from_list(execute.mboxes)
    prefetch_page_load_trace = get_response_tokens_from_object(prefetch.page_load)
    prefetch_views_trace = get_response_tokens_from_list(prefetch.views)
    prefetch_mbox_trace = get_response_tokens_from_list(prefetch.mboxes)

    analytics = [
        execute_page_load_trace,
        execute_mbox_trace,
        prefetch_page_load_trace,
        prefetch_views_trace,
        prefetch_mbox_trace
    ]

    result = flatten_list([item for item in analytics if item])
    return result or None


def get_response_meta(request, decisioning_method, decisioning_engine):
    """Get response metadata"""
    remote_mboxes = []
    remote_views = []

    if decisioning_engine:
        decisioning_dependency = decisioning_engine.has_remote_dependency(request)
        remote_mboxes = decisioning_dependency.get("remote_mboxes")
        remote_views = decisioning_dependency.get("remote_views")

    return {
        "decisioning_method": decisioning_method,
        "remote_mboxes": remote_mboxes,
        "remote_views": remote_views
    }


def process_response(session_id, cluster, request, response,
                     decisioning_method=DecisioningMethod.SERVER_SIDE.value, decisioning_engine=None):
    """Process Delivery API response
       :return (TargetDeliveryResponse) Returns response envelope
    """
    _id = response.id or VisitorId()
    edge_host = response.edge_host

    result = TargetDeliveryResponse(
        target_cookie=get_target_cookie(session_id, _id),
        target_location_hint_cookie=get_target_location_hint_cookie(cluster, edge_host),
        analytics_details=get_analytics_details(response),
        trace=get_trace_details(response),
        response_tokens=get_response_tokens(response),
        meta=get_response_meta(
            request,
            decisioning_method,
            decisioning_engine
        ),
        response=response)

    return remove_empty_values(result)
