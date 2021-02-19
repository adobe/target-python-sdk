# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Event Provider"""

class TargetEvent:
    def __init__(self, event_type, payload={}):
        self[event_type] = event_type
        for key in payload.keys():
            self[key] = payload.get(key)

class EventProvider:
    """EventProvider"""

    def __init__(self, events={}):
        """
        :param events: (dict.<str, callable>) An object with event name keys and callback
            function values, optional
        """
        self.subscriptions = {}
        self.subscription_count = 0
        for event_name in events.keys():
            self.subscribe(event_name, events.get(event_name))

    def subscribe(self, event_name, callback_func):
        """Subscribe to events
        :param event_name: (str) Event name, required
        callback_func: (callable) Callback function, required
        :return: (str)
        """
        self.subscription_count += 1
        if not self.subscriptions.get(event_name):
            self.subscriptions[event_name] = {}
        
        self.subscriptions[event_name][self.subscription_count] = callback_func
        return "{}:{}".format(event_name, self.subscription_count)
 
    def unsubscribe(self, id):
        """Unsubscribe from events
        :param id: (str) Event Id, required
        """
        event_name, event_id = id.split(":")
        if self.subscriptions.get(event_name):
            self.subscriptions[event_name][event_id]=None

    def emit(self, event_name, payload={}):
        """Emits events
        :param event_name: (str) Event name, required
        payload: (dict) Payload, optional
        """
        subscribed = self.subscriptions.get(event_name) or []
        for key, subscriber in subscribed.items():
            subscriber(TargetEvent(event_name, payload))