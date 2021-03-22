# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for tests/helpers.py"""
import unittest
from target_decisioning_engine.tests.helpers import get_test_artifacts
from target_decisioning_engine.tests.helpers import get_test_models


class TestHelpers(unittest.TestCase):

    def test_get_test_artifacts(self):
        test_artifacts = get_test_artifacts()
        self.assertGreater(len(list(test_artifacts)), 0)

    def test_get_test_models(self):
        test_models = list(get_test_models())
        self.assertGreater(len(list(test_models)), 0)
