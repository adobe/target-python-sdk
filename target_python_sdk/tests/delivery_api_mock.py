# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Mock out Delivery API calls"""
import json
import os


CURRENT_DIR = os.path.dirname(__file__)

MOCK_RESPONSES = {
    'default': './responses/default.json',
    'prefetch': './responses/prefetch.json',
    'execute': './responses/execute.json',
    'customer_ids': './responses/customer_ids.json',
    'invalid_request': './responses/invalid_request_error.json',
    'notifications': './responses/notifications.json'
}


def read_json_file(filename):
    """Read json file"""
    file_path = os.path.join(CURRENT_DIR, filename)
    _file = open(file_path, )
    data = json.load(_file)
    _file.close()
    return data


def setup_mock(response_key, responses, status=200):
    """Sets up mock response for Delivery API call"""
    filename = MOCK_RESPONSES.get(response_key)
    if not filename:
        return
    data = read_json_file(filename)

    responses.add('POST', '/rest/v1/delivery',
                  body=json.dumps(data), status=status,
                  content_type='application/json')
