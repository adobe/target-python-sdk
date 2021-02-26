# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""LimitedKeyDict class"""


class LimitedKeyDict(dict):
    """Dictionary class to be extended with an attribute map to limit the keys that can be set"""

    # TODO - TEST THIS CLASS
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    def _get_valid_keys(self):
        raise NotImplementedError()

    def _validate_kwargs_and_update(self, kwargs):
        if not kwargs:
            return {}
        valid = {key: value for (key, value) in kwargs.items() if key in self._get_valid_keys()}
        self.update(valid)

    def __setitem__(self, key, val):
        if key not in self._get_valid_keys():
            raise KeyError
        dict.__setitem__(self, key, val)
