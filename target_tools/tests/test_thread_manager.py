# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Test cases for ThreadManager"""
import unittest

from target_tools.thread_manager import ThreadManager


class TestThreadManager(unittest.TestCase):
    """TestThreadManager"""

    def setUp(self):
        self.thread_manager = None

    def tearDown(self):
        if self.thread_manager:
            self.thread_manager.close()
            ThreadManager._instance = None

    def test_init_throw_error(self):
        with self.assertRaises(RuntimeError) as err:
            ThreadManager()
            self.assertEqual(str(err.exception), "Must use ThreadManager.instance()")

    def test_close(self):
        self.thread_manager = ThreadManager.instance()
        self.assertIsNotNone(self.thread_manager.pool)
        self.assertIsNotNone(self.thread_manager._pool)

        self.thread_manager.close()
        self.assertIsNone(self.thread_manager._pool)

    def test_instance_returns_singleton(self):
        self.thread_manager = ThreadManager.instance()
        self.assertIsNotNone(self.thread_manager)

        thread_manager_2 = ThreadManager.instance()
        self.assertEqual(self.thread_manager, thread_manager_2)

    def test_instance_configure_number_of_threads(self):
        self.thread_manager = ThreadManager.instance(pool_threads=5)
        self.assertIsNotNone(self.thread_manager)
        self.assertEqual(self.thread_manager.pool_threads, 5)

    def test_pool_executes_asynchronous_function(self):
        def async_function(first, second="abc"):
            return "{}:{}".format(first, second)

        self.thread_manager = ThreadManager.instance()

        apply_async_args = (async_function,
                            (123,),
                            {"second": "xyz"})
        async_result = self.thread_manager.pool.apply_async(*apply_async_args)
        result = async_result.get()
        self.assertEqual(result, "123:xyz")
