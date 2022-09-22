# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for logger"""
import logging
import unittest
import six
import target_tools
from target_tools.logger import get_logger
from target_tools.logger import LOGGER_NAME

if six.PY3:
    try:
        import importlib
        reload = importlib.reload
    except ImportError:
        import imp # pylint: disable=deprecated-module
        reload = imp.reload
# else use builtin reload() for Python 2.7


def clear_logger_import_cache():
    """Clears singleton logger in a way that's back compat with older versions of python"""
    reload(target_tools.logger)


class TestLogger(unittest.TestCase):

    def setUp(self):
        clear_logger_import_cache()

    def tearDown(self):
        clear_logger_import_cache()

    def test_get_logger_default(self):
        # set root logger to INFO level since the default logger will propagate to it
        logging.basicConfig(level=logging.INFO)

        logger = get_logger()
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, LOGGER_NAME)
        self.assertEqual(logger.level, logging.INFO)
        logger.info("Nothing bad happened - just testing logger output")
        self.assertEqual(logger, get_logger())

    def test_get_logger_custom(self):
        custom_logger = logging.getLogger("custom")
        custom_logger.setLevel(logging.ERROR)

        logger = get_logger(logger=custom_logger)
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "custom")
        self.assertEqual(logger.level, logging.ERROR)

        logger.error("Nothing bad happened - just testing logger output")
        self.assertEqual(logger, get_logger())
