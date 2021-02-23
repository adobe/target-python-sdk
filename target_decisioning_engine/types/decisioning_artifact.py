# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""DecisioningArtifact model"""
from target_decisioning_engine.types.limited_key_dict import LimitedKeyDict


class RuleMeta(LimitedKeyDict):
    """RuleMeta"""
    
    __attribute_map = {
        "activity.id": "int",
        "activity.name": "str",
        "activity.type": "str",
        "audience.ids": "list<int>",
        "experience.id": "int",
        "experience.name": "str",
        "location.id": "int",
        "location.name": "str",
        "location.type": "str",
        "offer.id": "int",
        "offer.name": "str",
        "option.id": "int",
        "option.name": "str",
        "displayResponseType": "str"
    }

    def __init__(self, kwargs=None):
        """kwargs should only consist of keys inside __attribute_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return RuleMeta.__attribute_map.keys()


class Rule(LimitedKeyDict):
    """Rule"""

    __attribute_map = {
        "ruleKey": "str",
        "propertyTokens": "list<str>",
        "seed": "str",
        "condition": "dict",
        "consequence": "dict version of delivery_api_client.Model.mbox_response.MboxResponse"
    }

    def __init__(self, kwargs=None):
        """kwargs should only consist of keys inside __attribute_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return Rule.__attribute_map.keys()


class DecisioningArtifactMeta(LimitedKeyDict):
    """DecisioningArtifactMeta"""

    __attribute_map = {
        "generatedAt": "str",
        "organizationId": "str",
        "clientCode": "str",
        "workspace": "int",
        "environment": "str"
    }

    def __init__(self, kwargs=None):
        """kwargs should only consist of keys inside __attribute_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return DecisioningArtifactMeta.__attribute_map.keys()


class DecisioningArtifactRules(LimitedKeyDict):
    """DecisioningArtifactRules"""

    __attribute_map = {
        "mboxes": "dict<str: list<Rule>>",
        "views": "dict<str: list<Rule>>"
    }

    def __init__(self, kwargs=None):
        """kwargs should only consist of keys inside __attribute_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return DecisioningArtifactRules.__attribute_map.keys()


class DecisioningArtifact(LimitedKeyDict):
    """DecisioningArtifact"""

    __attribute_map = {
        "version": "str",
        "globalMbox": "str",
        "geoTargetingEnabled": "bool",
        "responseTokens": "list<str>",
        "remoteMboxes": "list<str>",
        "localMboxes": "list<str>",
        "remoteViews": "list<str>",
        "localViews": "list<str>",
        "meta": "DecisioningArtifactMeta",
        "rules": "DecisioningArtifactRules"
    }

    def __init__(self, kwargs=None):
        """kwargs should only consist of keys inside __attribute_map"""
        self._validate_kwargs_and_update(kwargs)

    def _get_valid_keys(self):
        return DecisioningArtifact.__attribute_map.keys()