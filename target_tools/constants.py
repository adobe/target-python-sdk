<<<<<<< HEAD
# Copyright 2020 Adobe. All rights reserved.
=======
# Copyright 2021 Adobe. All rights reserved.
>>>>>>> TNT-38924 getAttributes()
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Constants"""

<<<<<<< HEAD
<<<<<<< HEAD
DEFAULT_GLOBAL_MBOX = "target-global-mbox"
DEFAULT_NUM_FETCH_RETRIES = 10
DEFAULT_MAXIMUM_WAIT_READY = -1  # default is to wait indefinitely
=======
CHANNEL_TYPE = {
    'Mobile': "mobile",
    'Web': "web"
}
=======
#from delivery_api_client.src.Model.channel_type import ChannelType
>>>>>>> Per review comments - part 1

EMPTY_REQUEST = {
    'context': {
        'channel': 'Web' #ChannelType.WEB
    }
}
<<<<<<< HEAD
>>>>>>> TNT-38924 getAttributes()
=======

REQUEST_TYPES = ["prefetch", "execute"]
>>>>>>> Per review comments - part 1
