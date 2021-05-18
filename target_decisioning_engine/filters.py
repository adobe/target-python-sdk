# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""filters"""
from target_tools.utils import is_empty


def by_property_token(property_token):
    """
    :param property_token: (str) property token, required
    :return: (callable) Returns filter predicate
    """

    def _filter(rule):
        """
        :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) rule
        :return: (bool)
        """
        property_tokens = rule.get("propertyTokens", [])

        return is_empty(property_tokens) if not property_token else \
            (is_empty(property_tokens) or property_token in property_tokens)

    return _filter
