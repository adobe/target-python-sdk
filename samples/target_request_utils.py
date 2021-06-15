# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
import uuid
from delivery_api_client import Context
from delivery_api_client import ChannelType
from delivery_api_client import Address
from delivery_api_client import VisitorId
from target_python_sdk.cookies import TARGET_COOKIE
from target_python_sdk.cookies import LOCATION_HINT_COOKIE

TARGET_COOKIES = [
    TARGET_COOKIE,
    LOCATION_HINT_COOKIE
]


def get_cookie(cookies, cookie_name):
    return cookies.get(cookie_name)


def get_target_cookie(cookies):
    return get_cookie(cookies, TARGET_COOKIE)


def get_location_hint_cookie(cookies):
    return get_cookie(cookies, LOCATION_HINT_COOKIE)


def get_all_target_cookies(cookies=None):
    if not cookies:
        return []
    return [cookies.get(cookie_name) for cookie_name in TARGET_COOKIES if cookies.get(cookie_name)]


def set_cookie(response, cookie):
    response.set_cookie(cookie.get("name"), cookie.get("value"), max_age=cookie.get("maxAge"))


def set_target_cookies(response, target_delivery_response):
    target_cookie = target_delivery_response.get("target_cookie")
    if target_cookie:
        set_cookie(response, target_cookie)

    location_hint_cookie = target_delivery_response.get("target_location_hint_cookie")
    if location_hint_cookie:
        set_cookie(response, location_hint_cookie)


def get_address(request):
    return Address(url=request.url,
                   referring_url=request.referrer)


def get_context(request):
    return Context(channel=ChannelType.WEB,
                   time_offset_in_minutes=0,
                   address=get_address(request))


def get_visitor_id(request, customer_ids=None):
    tnt_id = request.args.get("tntId")
    third_party_id = request.args.get("thirdPartyId")
    mcid = request.args.get("mcid")
    return VisitorId(tnt_id=tnt_id or None,
                     third_party_id=third_party_id or None,
                     marketing_cloud_visitor_id=mcid or None,
                     customer_ids=customer_ids or None)


def get_uuid():
    return str(uuid.uuid4())


def initialize_options(request):
    target_cookie = get_target_cookie(request.cookies)
    location_hint_cookie = get_location_hint_cookie(request.cookies)

    return {
        "target_cookie": target_cookie,
        "location_hint_cookie": location_hint_cookie
    }
