<<<<<<< HEAD
# Copyright 2020 Adobe. All rights reserved.
=======
# Copyright 2021 Adobe. All rights reserved.
>>>>>>> AttributesProvider
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

<<<<<<< HEAD
<<<<<<< HEAD
"""Error and log messages"""

DECISIONING_ENGINE_NOT_READY = "Unable to fulfill request; decisioning engine not ready."


def attribute_not_exist(key_name, mbox_name):
    """Mbox attribute does not exist error string"""
    return "Attribute '{}' does not exist for mbox '{}'".format(key_name, mbox_name)


def property_token_mismatch(request_property, config_property):
    """Property token mismatch error string"""
    return "The property token specified in the request '{}' does not match the one specified in the config '{}'."\
        .format(request_property, config_property)
=======
=======
"""Error messages"""

>>>>>>> Fixed formatting to be consistent with pep8 and updated copyright to 2021
def attribute_not_exist(key_name, mbox_name):
    """Attribute not exist"""
    return "Attribute " + key_name + " does not exist for mbox " + mbox_name
>>>>>>> AttributesProvider
