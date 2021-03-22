# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Helper functions for testing"""
import json
import os

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


def get_client_options():
    """Returns mock options for TargetClient.create"""
    return {
        'client': 'testingclient',
        'organization_id': '11D1C9L459CE0AD80A495CBE@AdobeOrg'
    }


def spy_decorator(method_to_decorate):
    """Spies on an instance method when used with patch.object"""
    mock = MagicMock()

    def wrapper(_self, *args, **kwargs):
        mock(*args, **kwargs)
        return method_to_decorate(_self, *args, **kwargs)

    wrapper.mock = mock
    return wrapper


def read_json_file(directory, filename):
    """Read json file"""
    file_path = os.path.join(directory, filename)
    _file = open(file_path, )
    data = json.load(_file)
    _file.close()
    return data
