# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
import functools
import asyncio
from flask import Flask
from flask import request
from flask import Response
from samples.target_client_service import TargetClientService
from samples.target_request_utils import set_target_cookies
from samples.target_request_utils import get_uuid
from samples.target_request_utils import initialize_options
from delivery_api_client import MboxRequest
from delivery_api_client import ViewRequest
from delivery_api_client import Notification
from delivery_api_client import NotificationView
from delivery_api_client import MetricType
from delivery_api_client import NotificationMbox
from target_tools.utils import get_epoch_time_milliseconds
from target_python_sdk import TargetClient

app = Flask("__name__")


def client_ready_callback(ready_event):
    print("Server is now ready to start handling requests")


client_options = {
    "client": "acmeclient",
    "organization_id": "1234567890@AdobeOrg",
    "decisioning_method": "on-device",
    "events": {
        "client_ready": client_ready_callback
    }
}

target_client = TargetClient.create(client_options)
target_service = TargetClientService(target_client)
results = {}


@app.route('/executePageLoad', methods=['GET'])
def execute_page_load():
    """
    Make an execute pageload request to get all initial offers at page load time, get cookies for request if they exist,
    and on response set Target cookie for use with next request
    """
    get_offers_options = initialize_options(request)
    target_delivery_response = target_service.get_page_load_target_delivery_response(request, get_offers_options)
    response = Response(target_delivery_response.get("response").to_str(), status=200, mimetype='application/json')
    set_target_cookies(response, target_delivery_response)
    return response


@app.route('/executeMbox', methods=['GET'])
def execute_mbox():
    """
    Make an execute mboxes request, get cookies for request if they exist,
    and on response set Target cookie for use with next request
    """
    get_offers_options = initialize_options(request)

    mboxes = request.args.get("mbox", "")
    if not mboxes:
        return Response("No Content", status=204)

    execute_mboxes = [MboxRequest(name=mbox, index=index) for index, mbox in enumerate(mboxes.split(","))]
    target_delivery_response = target_service.get_mbox_target_delivery_response(request, get_offers_options,
                                                                                execute_mboxes=execute_mboxes)

    response = Response(target_delivery_response.get("response").to_str(), status=200, mimetype='application/json')
    set_target_cookies(response, target_delivery_response)
    return response


@app.route('/prefetchMbox', methods=['GET'])
def prefetch_mbox():
    """
    Make a single request that includes both execute mboxes request as well as prefetch mboxes request.
    Get cookies for request if they exist, and on response set Target cookie for use with next request
    """
    get_offers_options = initialize_options(request)

    mboxes = request.args.get("mbox", "")
    prefetch = request.args.get("prefetch", "")
    if not mboxes and not prefetch:
        return Response("No Content", status=204)

    execute_mboxes = [MboxRequest(name=mbox, index=index) for index, mbox in enumerate(mboxes.split(","))] \
        if mboxes else None
    prefetch_mboxes = [MboxRequest(name=mbox, index=index) for index, mbox in enumerate(prefetch.split(","))] \
        if prefetch else None
    target_delivery_response = target_service.get_mbox_target_delivery_response(request, get_offers_options,
                                                                                execute_mboxes=execute_mboxes,
                                                                                prefetch_mboxes=prefetch_mboxes)

    response = Response(target_delivery_response.get("response").to_str(), status=200, mimetype='application/json')
    set_target_cookies(response, target_delivery_response)
    return response


def get_offers_callback(request_id, target_delivery_response):
    response = Response(target_delivery_response.get("response").to_str(), status=200, mimetype='application/json')
    set_target_cookies(response, target_delivery_response)
    results[request_id] = response


def get_offers_err_callback(request_id, error):
    response = Response("Exception during get_offers call: {}".format(error), status=500, mimetype='application/json')
    results[request_id] = response


def get_target_delivery_response_async_callback(get_offers_options, request_id, views):
    get_offers_options["callback"] = functools.partial(get_offers_callback, request_id)
    get_offers_options["err_callback"] = functools.partial(get_offers_err_callback, request_id)

    async_result = target_service.prefetch_views_target_delivery_response(request,
                                                                          request_id,
                                                                          get_offers_options,
                                                                          views)
    async_result.wait()  # This is blocking, pass AsyncResult into an event loop
    return results.pop(request_id)


async def get_target_delivery_response_async_await(get_offers_options, request_id, views):
    target_delivery_response = await target_service.prefetch_views_target_delivery_response_asyncio(request,
                                                                                                    request_id,
                                                                                                    get_offers_options,
                                                                                                    views)
    response = Response(target_delivery_response.get("response").to_str(), status=200, mimetype='application/json')
    set_target_cookies(response, target_delivery_response)
    return response


def get_target_delivery_response(get_offers_options, request_id, views):
    target_delivery_response = target_service.prefetch_views_target_delivery_response(request,
                                                                                      request_id,
                                                                                      get_offers_options,
                                                                                      views)
    response = Response(target_delivery_response.get("response").to_str(), status=200, mimetype='application/json')
    set_target_cookies(response, target_delivery_response)
    return response


@app.route('/prefetchView', methods=['GET'])
def prefetch_view():
    """
    *** This usage is meant for Python 2.7, and uses callbacks for async execution since asyncio wasn't added until
    Python 3.5.

    Make a prefetch views request, get cookies for request if they exist,
    and on response set Target cookie for use with next request.  In this case, will run synchronously by default.  But
    if async execution is specified then the result is returned to the callback and an AsyncResult object is returned
    from the TargetClient.get_offers call - which must be used for thread coordination
    """
    request_id = get_uuid()
    get_offers_options = initialize_options(request)

    views = request.args.get("view", "")
    do_async = bool(request.args.get("async", False))
    if not views:
        return Response("No Content", status=204)

    view_requests = [ViewRequest(name=view) for view in views.split(",")]
    return get_target_delivery_response_async_callback(get_offers_options, request_id, view_requests) if do_async else \
        get_target_delivery_response(get_offers_options, request_id, view_requests)


@app.route('/prefetchViewAsyncio', methods=['GET'])
def prefetch_view_asyncio():
    """
    *** This usage is meant for Python 3.5+, and uses asyncio for async execution.

    Make a prefetch views request, get cookies for request if they exist,
    and on response set Target cookie for use with next request.  In this case, will run synchronously by default.  But
    if async execution is specified then downstream functions must be chained together using async keyword so they are
    handled properly by the asyncio event loop.
    """
    request_id = get_uuid()
    get_offers_options = initialize_options(request)

    views = request.args.get("view", "")
    do_async = bool(request.args.get("async", False))
    if not views:
        return Response("No Content", status=204)

    view_requests = [ViewRequest(name=view) for view in views.split(",")]
    return asyncio.run(get_target_delivery_response_async_await(get_offers_options, request_id, view_requests)) if \
        do_async else get_target_delivery_response(get_offers_options, request_id, view_requests)


def _get_all_view_notifications(views):
    notifications = []
    for view in views:
        tokens = view.get("event_tokens")
        notifications.append(Notification(id=get_uuid(),
                                          impression_id=get_uuid(),
                                          view=NotificationView(key=view.get("key"),
                                                                name=view.get("name"),
                                                                state=view.get("state")),
                                          type=MetricType.DISPLAY,
                                          timestamp=get_epoch_time_milliseconds(),
                                          tokens=tokens))
    return notifications


def _get_all_mbox_notifications(mboxes):
    notifications = []
    for mbox in mboxes:
        tokens = mbox.get("event_tokens")
        notifications.append(Notification(id=get_uuid(),
                                          impression_id=get_uuid(),
                                          mbox=NotificationMbox(name=mbox.get("name"), state=mbox.get("state")),
                                          type=MetricType.DISPLAY,
                                          timestamp=get_epoch_time_milliseconds(),
                                          tokens=tokens))
    return notifications


@app.route('/sendNotifications', methods=['POST'])
def send_notifications():
    """
    Takes a payload based on response from a prefetch request (in json format) from previous get_offers call, converts
    it to a PrefetchResponse object, uses it to create DeliveryRequest with notifications, and makes a
    send_notifications call. This implementation makes a synchronous call, but async execution is supported via ether
    callback or asyncio's async/await.  See prefetch_view() and prefetch_view_asyncio() above for examples of
    both async implementations.
    """
    send_notifications_options = initialize_options(request)
    notifications_dict = request.get_json(force=True)

    notifications = []
    if notifications_dict.get("views"):
        notifications.extend(_get_all_view_notifications(notifications_dict.get("views")))
    if notifications_dict.get("mboxes"):
        notifications.extend(_get_all_mbox_notifications(notifications_dict.get("mboxes")))

    target_delivery_response = target_service.send_notifications(request, send_notifications_options, notifications)

    response = Response(target_delivery_response.get("response").to_str(), status=200, mimetype='application/json')
    set_target_cookies(response, target_delivery_response)
    return response
