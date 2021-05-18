# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""perf tool"""
import sys
from target_tools.utils import get_epoch_time_milliseconds


this = sys.modules[__name__]
this.perf_tool_instance = None


class _PerfTool:
    """PerfTool"""

    def __init__(self):
        """PerfTool initialization"""
        self.timing_ids = {}
        self.start_times = {}
        self.timings = {}

    def _get_unique_timing_id(self, _id):
        """
        :param _id: (str) metric name
        :return: (str) unique ID
        """
        count = self.timing_ids.get(_id, 0) + 1
        self.timing_ids[_id] = count
        return "{}{}".format(_id, count)

    def time_start(self, _id, increment_timer=False):
        """Sets start time for ID
        :param _id: (str) metric name
        :param increment_timer: (bool) increment timer, defaults to False
        :return: (str) ID
        """
        timing_id = self._get_unique_timing_id(_id) if increment_timer else _id
        if timing_id not in self.start_times:
            self.start_times[timing_id] = get_epoch_time_milliseconds()
        return timing_id

    def time_end(self, _id, offset=0):
        """Sets timing for ID
        :param _id: (str) timing_id that must match the output from time_start
        :param offset: (int) timing offset, defaults to 0
        :return: (int) timing
        """
        if not self.start_times.get(_id):
            return -1
        timing = get_epoch_time_milliseconds() - self.start_times.get(_id) - offset
        self.timings[_id] = timing
        return timing

    def reset(self):
        """Resets all timings and IDs"""
        self.timing_ids = {}
        self.start_times = {}
        self.timings = {}

    def get_timing(self, key):
        """Returns timing for a given ID
        :param key: (str) ID
        :return: (int) timing
        """
        return self.timings.get(key)

    def get_timings(self):
        """Returns all timings"""
        return self.timings


def get_perf_tool_instance():
    """Creates or gets singleton instance of _PerfTool"""
    if not this.perf_tool_instance:
        this.perf_tool_instance = _PerfTool()
    return this.perf_tool_instance
