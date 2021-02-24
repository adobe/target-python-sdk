# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Unit tests for target_decisioning_engine.utils module"""
# pylint: disable=too-many-arguments
import unittest
from target_decisioning_engine.types.decisioning_artifact import DecisioningArtifact
from target_decisioning_engine.utils import parse_url
from target_decisioning_engine.utils import has_remote_dependency
from target_python_sdk.tests.delivery_request_setup import create_delivery_request
from target_tools.constants import EMPTY_STRING


class TestUtils(unittest.TestCase):
    """TestUtils"""

    def validate_parse_url(self, result, url, path, query, fragment, domain, subdomain, top_level_domain):
        """Validate parsed url parts"""
        self.assertEqual(result.get("url"), url)
        self.assertEqual(result.get("path"), path)
        self.assertEqual(result.get("query"), query)
        self.assertEqual(result.get("fragment"), fragment)
        self.assertEqual(result.get("domain"), domain)
        self.assertEqual(result.get("subdomain"), subdomain)
        self.assertEqual(result.get("top_level_domain"), top_level_domain)

    def test_parse_url_host_length_1(self):
        url = "http://myfavesite/posts?page=1#bottom"
        result = parse_url(url)
        self.validate_parse_url(result, url, "/posts", "page=1", "bottom", "myfavesite",
                                EMPTY_STRING, EMPTY_STRING)

    def test_parse_url_host_length_2(self):
        url = "http://myfavesite.com/posts?page=1#bottom"
        result = parse_url(url)
        self.validate_parse_url(result, url, "/posts", "page=1", "bottom", "myfavesite.com",
                                EMPTY_STRING, "com")

    def test_parse_url_host_length_3(self):
        url = "http://www.myfavesite.com/posts?page=1#bottom"
        result = parse_url(url)
        self.validate_parse_url(result, url, "/posts", "page=1", "bottom", "www.myfavesite.com",
                                EMPTY_STRING, "com")

    def test_parse_url_host_length_4(self):
        url = "http://blog.myfavesite.geocities.com/posts?page=1#bottom"
        result = parse_url(url)
        self.validate_parse_url(result, url, "/posts", "page=1", "bottom", "blog.myfavesite.geocities.com",
                                "blog", "geocities.com")

    def test_has_remote_dependency_no_artifact(self):
        with self.assertRaises(Exception) as err:
            has_remote_dependency(None, None)
        self.assertEqual(str(err.exception), "The decisioning artifact is not available")

    def test_has_remote_dependency_mboxes_and_views(self):
        request_opts = {
            "execute": {
                "mboxes": [{
                    "name": "mbox1"
                }, {
                    "name": "mbox2"
                }]
            },
            "prefetch": {
                "mboxes": [{
                    "name": "mbox3"
                }],
                "views": [{
                    "name": "view1"
                }, {
                    "name": "view2"
                }, {
                    "name": "view3"
                }]
            }
        }
        request = create_delivery_request(request_opts)

        remote_mboxes = ["mbox1"]
        local_mboxes = ["mbox2"]
        remote_views = ["view1"]
        local_views = ["view2"]
        artifact = DecisioningArtifact({"remoteMboxes": remote_mboxes,
                                        "localMboxes": local_mboxes,
                                        "remoteViews": remote_views,
                                        "localViews": local_views
                                        })

        result = has_remote_dependency(artifact, request)

        self.assertEqual(result.get("remote_needed"), True)
        self.assertEqual(result.get("remote_mboxes"), {"mbox1", "mbox3"})
        self.assertEqual(result.get("remote_views"), {"view1", "view3"})
