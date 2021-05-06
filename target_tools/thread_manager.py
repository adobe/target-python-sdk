# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""ThreadManager for managing async requests"""
# pylint: disable=attribute-defined-outside-init
# pylint: disable=no-member
import atexit
from multiprocessing.pool import ThreadPool


class ThreadManager(object):
    """ThreadManager"""
    _instance = None

    def __init__(self):
        raise RuntimeError("Must use ThreadManager.instance()")

    def close(self):
        """Cleanup"""
        if self._pool:
            self._pool.close()
            self._pool.join()
            self._pool = None
            if hasattr(atexit, 'unregister'):
                atexit.unregister(self.close)

    @classmethod
    def instance(cls, pool_threads=1):
        """Use ThreadManager.instance() to return singleton instance"""
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.pool_threads = pool_threads
            cls._instance._pool = None
        return cls._instance

    @property
    def pool(self):
        """ThreadManager instance attribute used to access the ThreadPool"""
        if self._pool is None:
            atexit.register(self.close)
            self._pool = ThreadPool(self.pool_threads)
        return self._pool
