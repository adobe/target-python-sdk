# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""NotificationProvider class"""
import threading

from delivery_api_client import Notification
from delivery_api_client import DeliveryRequest
from delivery_api_client import Telemetry
from delivery_api_client import NotificationMbox
from delivery_api_client import MetricType
from delivery_api_client import TelemetryFeatures
from delivery_api_client import DecisioningMethod
from target_decisioning_engine.constants import LOG_PREFIX
from target_tools.utils import get_epoch_time_milliseconds
from target_tools.utils import create_uuid
from target_tools.logger import get_logger
from target_tools.utils import noop

LOG_TAG = "{}.NotificationProvider".format(LOG_PREFIX)


class NotificationProvider:
    """NotificationProvider"""

    def __init__(self, request, visitor, send_notification_func=noop, telemetry_enabled=True):
        """
        :param request: (delivery_api_client.Model.delivery_request.DeliveryRequest) request
        :param visitor: (delivery_api_client.Model.visitor_id.VisitorId) VisitorId instance
        :param send_notification_func: (callable) function used to send the notification
        :param telemetry_enabled: (bool) is telemetry enabled
        """
        self.visitor = visitor
        self.send_notification_func = send_notification_func
        self.telemetry_enabled = telemetry_enabled
        self.request = request
        self.request_id = request.request_id
        self.prev_event_keys = set()
        self.notifications = []
        self.telemetry_entries = []
        self.logger = get_logger()

    def add_notification(self, mbox, trace_func=noop):
        """
        :param mbox: (delivery_api_client.Model.mbox_response.MboxResponse) mbox
        :param trace_func: (callable) trace function
        """
        display_tokens = []
        for option in mbox.options:
            event_token = option.event_token
            event_key = "{}-{}".format(mbox.name, event_token)

            if event_token and event_key not in self.prev_event_keys:
                display_tokens.append(event_token)
                self.prev_event_keys.add(event_key)

        if not display_tokens:
            return

        notification_mbox = NotificationMbox(name=mbox.name)
        notification = Notification(id=create_uuid(),
                                    impression_id=create_uuid(),
                                    timestamp=get_epoch_time_milliseconds(),
                                    type=MetricType.DISPLAY,
                                    mbox=notification_mbox,
                                    tokens=display_tokens)
        if callable(trace_func):
            trace_func(notification)

        self.notifications.append(notification)

    def add_telemetry_entry(self, entry):
        """
        :param entry: (delivery_api_client.Model.telemetry_entry.TelemetryEntry) telemetry entry
        """
        if not self.telemetry_enabled:
            return

        entry.request_id = self.request_id
        entry.timestamp = get_epoch_time_milliseconds()
        entry.features = TelemetryFeatures(decisioning_method=DecisioningMethod.ON_DEVICE)
        self.telemetry_entries.append(entry)

    def send_notifications(self):
        """Send notifications via the send_notification_func"""
        self.logger.debug("{}.send_notifications - Notifications: {} \nTelemetry Entries: {}"
                          .format(LOG_TAG, self.notifications, self.telemetry_entries))

        if not self.notifications and not self.telemetry_entries:
            return

        _id = self.request.id
        context = self.request.context
        experience_cloud = self.request.experience_cloud

        notifications = self.notifications if self.notifications else None
        telemetry = Telemetry(entries=self.telemetry_entries) if self.telemetry_entries else None
        request = DeliveryRequest(id=_id, context=context, experience_cloud=experience_cloud,
                                  notifications=notifications, telemetry=telemetry)
        send_notification_opts = {
            "request": request,
            "visitor": self.visitor
        }

        async_send = threading.Thread(target=self.send_notification_func, args=(send_notification_opts,))
        async_send.start()
        self.notifications = []
        self.telemetry_entries = []
