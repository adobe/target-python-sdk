# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Constants"""
from delivery_api_client import ChannelType
from delivery_api_client import DeliveryRequest
from delivery_api_client import Context

DEFAULT_GLOBAL_MBOX = "target-global-mbox"
DEFAULT_NUM_FETCH_RETRIES = 10
DEFAULT_MAXIMUM_WAIT_READY = -1  # default is to wait indefinitely

EMPTY_REQUEST = DeliveryRequest(context=Context(channel=ChannelType.WEB))
REQUEST_TYPES = ["prefetch", "execute"]

ENVIRONMENT_PROD = "production"
ENVIRONMENT_STAGE = "staging"
ENVIRONMENT_DEV = "development"
POSSIBLE_ENVIRONMENTS = [
  ENVIRONMENT_PROD,
  ENVIRONMENT_STAGE,
  ENVIRONMENT_DEV
]

EMPTY_STRING = ""
MILLISECONDS_IN_SECOND = 1000
