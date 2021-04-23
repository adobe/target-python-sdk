# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Testing helper functions for transforming dicts to DeliveryRequest models"""
from delivery_api_client import VisitorId
from delivery_api_client import Trace
from delivery_api_client import CustomerId
from delivery_api_client import Context
from delivery_api_client import Geo
from delivery_api_client import Browser
from delivery_api_client import Window
from delivery_api_client import Screen
from delivery_api_client import Application
from delivery_api_client import MobilePlatform
from delivery_api_client import Address
from delivery_api_client import ExperienceCloud
from delivery_api_client import AnalyticsRequest
from delivery_api_client import AudienceManager
from delivery_api_client import ExecuteRequest
from delivery_api_client import Order
from delivery_api_client import Product
from delivery_api_client import MboxRequest
from delivery_api_client import ViewRequest
from delivery_api_client import RequestDetails as PageLoad
from delivery_api_client import PrefetchRequest
from delivery_api_client import DeliveryRequest
from delivery_api_client import Notification
from delivery_api_client import ChannelType
from delivery_api_client import ModelProperty as Property


def create_customer_id(customer_id):
    """Create new CustomerId object"""
    return CustomerId(id=customer_id.get("id"),
                      integration_code=customer_id.get("integrationCode"),
                      authenticated_state=customer_id.get("authenticatedState"))


def create_customer_ids(customer_ids):
    """Create list of CustomerId objects"""
    if not customer_ids:
        return None
    return [create_customer_id(customer_id) for customer_id in customer_ids]


def create_visitor_id(_id):
    """Creates new VisitorId"""
    if not _id:
        return None

    return VisitorId(
        tnt_id=_id.get('tntId'),
        third_party_id=_id.get('thirdPartyId'),
        marketing_cloud_visitor_id=_id.get('marketingCloudVisitorId'),
        customer_ids=create_customer_ids(_id.get('customerIds'))
    )


def create_property(_property):
    """Create new Property"""
    return Property(**_property) if _property else None


def create_mobile_platform(mobile_platform):
    """Create new MobilePlatform"""
    return MobilePlatform(**mobile_platform) if mobile_platform else None


def create_application(application):
    """Create new Application"""
    return Application(**application) if application else None


def create_screen(screen):
    """Create new Screen"""
    return Screen(**screen) if screen else None


def create_window(window):
    """Create new Window"""
    return Window(**window) if window else None


def create_browser(browser):
    """Create new Browser"""
    return Browser(**browser) if browser else None


def create_geo(geo):
    """Create new Geo"""
    if not geo:
        return None

    return Geo(ip_address=geo.get("ipAddress"),
               latitude=geo.get("latitude"),
               longitude=geo.get("longitude"),
               country_code=geo.get("countryCode"),
               state_code=geo.get("stateCode"),
               city=geo.get("city"),
               zip=geo.get("zip"))


def create_address(address):
    """Create new Address"""
    return Address(url=address.get("url"),
                   referring_url=address.get("referringUrl")) if address else None


def create_context(context):
    """Create new Context"""
    if not context:
        context = {}

    return Context(channel=context.get('channel') or ChannelType.WEB,
                   mobile_platform=create_mobile_platform(context.get('mobilePlatform')),
                   application=create_application(context.get('application')),
                   screen=create_screen(context.get('screen')),
                   window=create_window(context.get('window')),
                   browser=create_browser(context.get('browser')),
                   address=create_address(context.get('address')),
                   geo=create_geo(context.get('geo')),
                   user_agent=context.get('userAgent'))


def create_analytics(analytics):
    """Create new AnalyticsRequest"""
    return AnalyticsRequest(**analytics) if analytics else None


def create_audience_manager(audience_manager):
    """Create new AudienceManager"""
    return AudienceManager(**audience_manager) if audience_manager else None


def create_experience_cloud(experience_cloud):
    """Create new ExperienceCloud"""
    if not experience_cloud:
        return None

    return ExperienceCloud(
        analytics=create_analytics(experience_cloud.get('analytics')),
        audience_manager=create_audience_manager(experience_cloud.get('audienceManager'))
    )


def create_order(order):
    """Create new Order"""
    return Order(**order) if order else None


def create_product(product):
    """Create new Product"""
    return Product(id=product.get("id"),
                   category_id=product.get("categoryId")) if product else None


def create_view(view):
    """Create new ViewRequest"""
    if not view:
        return None
    return ViewRequest(address=create_address(view.get('address')),
                       parameters=view.get('parameters'),
                       profile_parameters=view.get('profileParameters'),
                       order=create_order(view.get('order')),
                       product=create_product(view.get('product')),
                       name=view.get('name'),
                       key=view.get('key'))


def create_views(views):
    """Creates list of ViewRequest objects"""
    if not views:
        return None

    result_views = [create_view(view) for view in views]
    return result_views or None


def create_page_load(page_load):
    """Create new PageLoad"""
    if not page_load:
        return None
    return PageLoad(address=create_address(page_load.get('address')),
                    parameters=page_load.get('parameters'),
                    profile_parameters=page_load.get('profileParameters'),
                    order=create_order(page_load.get('order')),
                    product=create_product(page_load.get('product')))


def create_mbox(mbox, index):
    """Create new MboxRequest"""
    if not mbox:
        return None
    return MboxRequest(address=create_address(mbox.get('address')),
                       parameters=mbox.get('parameters'),
                       profile_parameters=mbox.get('profileParameters'),
                       order=create_order(mbox.get('order')),
                       product=create_product(mbox.get('product')),
                       index=mbox.get('index') if mbox.get('index') else index,
                       name=mbox.get('name'))


def create_mboxes(mboxes):
    """Creates list of MboxRequest objects"""
    if not mboxes:
        return None

    result_mboxes = [create_mbox(mbox, index) for index, mbox in enumerate(mboxes)]
    return result_mboxes or None


def create_execute(execute):
    """Create new ExecuteRequest"""
    if not execute:
        return None

    page_load = execute.get('pageLoad')
    mboxes = execute.get('mboxes')

    return ExecuteRequest(
        page_load=create_page_load(page_load) if page_load else None,
        mboxes=create_mboxes(mboxes) if mboxes else None
    )


def create_prefetch(prefetch):
    """Create new PrefetchRequest"""
    if not prefetch:
        return None

    page_load = prefetch.get('pageLoad')
    views = prefetch.get('views')
    mboxes = prefetch.get('mboxes')

    return PrefetchRequest(
        page_load=create_page_load(page_load) if page_load else None,
        views=create_views(views) if views else None,
        mboxes=create_mboxes(mboxes) if mboxes else None
    )


def create_notification(notification):
    """Create new Notification"""
    _id, _type, timestamp, impression_id, tokens, mbox, view = \
        [notification.get(key) for key in ['id', 'type', 'timestamp', 'impressionId', 'tokens', 'mbox', 'view']]

    return Notification(
        id=_id,
        type=_type,
        timestamp=timestamp,
        impression_id=impression_id,
        tokens=tokens,
        mbox=mbox,
        view=view
    )


def create_notifications(notifications):
    """Creates list of Notification objects"""
    if not notifications:
        return None

    result_notifications = [create_notification(notification) for notification in notifications]
    return result_notifications or None


def create_trace(trace):
    """Creates Trace object"""
    return Trace(authorization_token=trace.get("authorizationToken", ""),
                 usage=trace.get("usage")) if trace is not None else None


def create_delivery_request(request_dict):
    """Create new DeliveryRequest from request dict"""
    _id = create_visitor_id(request_dict.get('id'))
    _property = create_property(request_dict.get('property'))
    context = create_context(request_dict.get('context'))
    experience_cloud = create_experience_cloud(request_dict.get('experienceCloud'))
    execute = create_execute(request_dict.get('execute'))
    prefetch = create_prefetch(request_dict.get('prefetch'))
    notifications = create_notifications(request_dict.get('notifications'))
    trace = create_trace(request_dict.get('trace'))
    request_id = request_dict.get("requestId")
    qa_mode = request_dict.get("qa_mode")
    preview = request_dict.get("preview")
    delivery_request = DeliveryRequest(id=_id, _property=_property, context=context,
                                       experience_cloud=experience_cloud, execute=execute,
                                       prefetch=prefetch, notifications=notifications, trace=trace,
                                       request_id=request_id, qa_mode=qa_mode, preview=preview)
    return delivery_request
