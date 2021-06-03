# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Output logger"""
import logging
import sys

LOGGER_NAME = "adobe.target"

this = sys.modules[__name__]
this.LOG = None


def get_logger(logger=None):
    """Returns singleton logger for sdk. By default, propagates to root logger at INFO level
    :param logger: (Logger) User-provided logger that overrides default for entire sdk
    :return: (Logger) Singleton logger for use throughout the sdk
    """
    if this.LOG:
        return this.LOG

    if logger:
        this.LOG = logger
    else:
        this.LOG = logging.getLogger(LOGGER_NAME)
        this.LOG.setLevel(logging.INFO)

    return this.LOG
