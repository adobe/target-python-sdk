# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""On Device Decisioning constants"""
from target_tools.constants import ENVIRONMENT_PROD
from target_tools.constants import ENVIRONMENT_STAGE
from target_tools.constants import ENVIRONMENT_DEV

DEFAULT_POLLING_INTERVAL = 300  # five minutes (in seconds)
MINIMUM_POLLING_INTERVAL = 300  # five minutes (in seconds)
NUM_FETCH_RETRIES = 10
SUPPORTED_ARTIFACT_MAJOR_VERSION = 1
SUPPORTED_ARTIFACT_OBFUSCATION_VERSION = 1

ARTIFACT_FILENAME = "rules.json"

LOG_PREFIX = "LD"

CDN_BASE_PROD = "assets.adobetarget.com"
CDN_BASE_STAGE = "assets.staging.adobetarget.com"
CDN_BASE_DEV = "assets.staging.adobetarget.com"

HTTP_HEADER_FORWARDED_FOR = "x-forwarded-for"
HTTP_HEADER_GEO_LATITUDE = "x-geo-latitude"
HTTP_HEADER_GEO_LONGITUDE = "x-geo-longitude"
HTTP_HEADER_GEO_COUNTRY = "x-geo-country-code"
HTTP_HEADER_GEO_REGION = "x-geo-region-code"
HTTP_HEADER_GEO_CITY = "x-geo-city"

CDN_BASE = {
    ENVIRONMENT_PROD: CDN_BASE_PROD,
    ENVIRONMENT_STAGE: CDN_BASE_STAGE,
    ENVIRONMENT_DEV: CDN_BASE_DEV
}

CAMPAIGN_BUCKET_SALT = "0"

# Response token keys
AUDIENCE_IDS = "audience.ids"
ACTIVITY_DECISIONING_METHOD = "activity.decisioningMethod"
ACTIVITY_ID = "activity.id"
ACTIVITY_NAME = "activity.name"
ACTIVITY_TYPE = "activity.type"
EXPERIENCE_ID = "experience.id"
EXPERIENCE_NAME = "experience.name"
LOCATION_ID = "location.id"
LOCATION_NAME = "location.name"
LOCATION_TYPE = "location.type"
OFFER_ID = "offer.id"
OFFER_NAME = "offer.name"
OPTION_ID = "option.id"
OPTION_NAME = "option.name"
GEO_CITY = "geo.city"
GEO_COUNTRY = "geo.country"
GEO_STATE = "geo.state"
GEO_LATITUDE = "geo.latitude"
GEO_LONGITUDE = "geo.longitude"

NOT_MODIFIED = 304
OK = 200
PARTIAL_CONTENT = 206
BAD_REQUEST = 400
FORBIDDEN = 403
HTTP_GET = "GET"
