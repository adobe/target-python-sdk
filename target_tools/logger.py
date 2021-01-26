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

LOGGER_NAME = 'adobe.target'
LOG = logging.getLogger(LOGGER_NAME)


<<<<<<< HEAD
def get_logger():
    """Returns singleton logger for sdk"""
=======
def get_logger(logger=None):
    """Returns standard root logger for now"""
<<<<<<< HEAD
    print logger
>>>>>>> Fixed formatting to be consistent with pep8 and updated copyright to 2021
=======
    print(logger)
>>>>>>> Put back parenthesis to satisfy linter
    return LOG
