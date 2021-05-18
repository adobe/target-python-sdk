# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Helper functions for deriving various info from client"""
from user_agents import parse
from target_tools.utils import parse_int

OTHER = "Other"
UNKNOWN = "Unknown"
DESKTOP = "Desktop"


def browser_from_user_agent(user_agent=None):
    """Use regex to determine browser from the user agent
    :param user_agent: (str) user agent
    :return: (dict{"name": str, "version": int})
    """
    if not user_agent:
        user_agent = ""

    agent_obj = parse(user_agent)
    major_version = parse_int(agent_obj.browser.version_string.split(".")[0])\
        if agent_obj.browser.version_string else -1

    return {
        "name": agent_obj.browser.family if agent_obj.browser.family != OTHER else UNKNOWN,
        "version": major_version
    }


def operating_system_from_user_agent(user_agent):
    """Get OS from user agent
    :param user_agent: (str) user agent
    :return: (str) OS name
    """
    agent_obj = parse(user_agent)
    return agent_obj.os.family if agent_obj.os.family != OTHER else UNKNOWN


def device_type_from_user_agent(user_agent):
    """Gets device type from user agent
    :param user_agent: (str) browser user agent
    :return: (str) user device type
    """
    agent_obj = parse(user_agent)
    return agent_obj.device.family if agent_obj.device.family != OTHER else DESKTOP
