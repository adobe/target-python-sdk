# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Helper functions for testing"""
# pylint: disable=unused-argument
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
import json
import os
from target_python_sdk.utils import is_dict
from target_python_sdk.utils import is_string
from target_python_sdk.utils import is_number
from target_python_sdk.utils import is_list


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
    with open(file_path) as _file:
        data = json.load(_file)
        _file.close()
        return data


def _default_parse_handler(key, value):
    """Default parse handler for object traversal"""
    return value


def traverse_object(obj=None, result=None, parse_handler=_default_parse_handler):
    """Traverses dict obj and constructs a new dict by executing parse_handler for each dict entry"""
    if is_dict(result):
        for key, val in obj.items():
            if is_list(val) or is_dict(val):
                result[key] = traverse_object(val, [] if is_list(val) else {}, parse_handler)
            else:
                result[key] = parse_handler(key, val)
    elif is_list(result):
        for key, val in enumerate(obj):
            if is_list(val) or is_dict(val):
                result.append(traverse_object(val, [] if is_list(val) else {}, parse_handler))
            else:
                result.append(parse_handler(key, val))

    return result


def assert_object(value):
    """Throws AssertionError if value is not an object"""
    assert isinstance(value, object), "'{}' is not an object".format(value)


def assert_string(value):
    """Throws AssertionError if value is not a str"""
    assert is_string(value), "'{}' is not a string".format(value)


def assert_number(value):
    """Throws AssertionError if value is not an int"""
    assert is_number(value), "'{}' is not a number".format(value)


def prepare_test_response(response=None):
    """Traverses expected response and sets custom matchers for dynamic values"""
    if not response:
        response = {}

    specials = {
        "expect.any(Object)": assert_object,
        "expect.any(String)": assert_string,
        "expect.any(Number)": assert_number
    }

    def _special_value_handler(key, value):
        """Gets custom matcher function"""
        return specials.get(value, value)

    return traverse_object(response, {}, _special_value_handler)


def is_json(filename):
    """Predicate for checking if a filename is .json"""
    return filename.lower().endswith(".json")


def expect_to_match_object(received, expected):
    """Validates received response against expected response"""
    expected = prepare_test_response(expected)

    if received is None:
        assert expected is None, "None value received, but expected '{}'".format(expected)

    for key, value in expected.items():
        if callable(value):
            value(received.get(key))
        elif is_dict(value):
            expect_to_match_object(received.get(key), value)
        elif is_list(value):
            for index, item in enumerate(value):
                received_item = received.get(key)[index] if received.get(key) else None
                if callable(item):
                    item(received_item)
                elif is_dict(item):
                    expect_to_match_object(received_item, item or {})
                else:
                    assert item == received_item, \
                        "Received list item '{}' does not equal expected list item '{}'" \
                        .format(str(received_item), str(item))
        else:
            assert value == received.get(key), \
                "Received value '{}' for key '{}' does not equal expected value '{}'" \
                .format(received.get(key), key, value)
