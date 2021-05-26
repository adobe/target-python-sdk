# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Unit tests for target_decisioning_engine.utils module"""
import unittest
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock
from target_decisioning_engine.types.decisioning_artifact import DecisioningArtifact
from target_decisioning_engine.types.decisioning_config import DecisioningConfig
from target_decisioning_engine.utils import parse_url
from target_decisioning_engine.utils import determine_artifact_location
from target_decisioning_engine.utils import has_remote_dependency
from target_tools.tests.delivery_request_setup import create_delivery_request
from target_tools.constants import EMPTY_STRING
from target_tools.constants import ENVIRONMENT_DEV
from target_tools.constants import ENVIRONMENT_STAGE


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
        self.assertEqual(result.get("topLevelDomain"), top_level_domain)

    def test_parse_url_missing_top_level_domain(self):
        url = "http://myfavesite/posts?page=1#bottom"
        result = parse_url(url)
        self.validate_parse_url(result, url, EMPTY_STRING, EMPTY_STRING, EMPTY_STRING, EMPTY_STRING,
                                EMPTY_STRING, EMPTY_STRING)

    def test_parse_url_without_subdomain(self):
        url = "http://myfavesite.com/posts?page=1#bottom"
        result = parse_url(url)
        self.validate_parse_url(result, url, "/posts", "page=1", "bottom", "myfavesite",
                                EMPTY_STRING, "com")

    def test_parse_url_with_subdomain(self):
        url = "http://www.myfavesite.com"
        result = parse_url(url)
        self.validate_parse_url(result, url, EMPTY_STRING, EMPTY_STRING, EMPTY_STRING, "myfavesite",
                                "www", "com")

    def test_parse_url_with_subdomain_path_param_anchor(self):
        url = "http://www.myfavesite.com/posts?page=1#bottom"
        result = parse_url(url)
        self.validate_parse_url(result, url, "/posts", "page=1", "bottom", "myfavesite",
                                "www", "com")

    def test_parse_url_with_multi_part_subdomain(self):
        url = "http://blog.myfavesite.geocities.com/posts?page=1#bottom"
        result = parse_url(url)
        self.validate_parse_url(result, url, "/posts", "page=1", "bottom", "geocities",
                                "blog.myfavesite", "com")

    def test_parse_url_with_multi_part_top_level_domain(self):
        url = "http://some.subdomain.google.co.uk"
        result = parse_url(url)
        self.validate_parse_url(result, url, EMPTY_STRING, EMPTY_STRING, EMPTY_STRING, "google",
                                "some.subdomain", "co.uk")


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
        self.assertEqual(set(result.get("remote_mboxes")), set(["mbox1", "mbox3"]))
        self.assertEqual(set(result.get("remote_views")), set(["view1", "view3"]))

    def test_determine_artifact_location(self):
        config = DecisioningConfig("MyClient", "12345@AdobeOrg", environment=ENVIRONMENT_DEV,
                                   cdn_environment=ENVIRONMENT_STAGE)
        artifact_location = determine_artifact_location(config)
        self.assertEqual(artifact_location,
                         "https://assets.staging.adobetarget.com/MyClient/development/v1/rules.json")

    def test_determine_artifact_location_invalid_env(self):
        config = DecisioningConfig("MyClient", "12345@AdobeOrg", environment="bad")
        mock_logger = Mock()
        with patch("target_decisioning_engine.utils.logger", mock_logger):
            artifact_location = determine_artifact_location(config)
            self.assertEqual(artifact_location,
                             "https://assets.adobetarget.com/MyClient/production/v1/rules.json")
            self.assertEqual(mock_logger.debug.call_count, 1)
            self.assertEqual(mock_logger.debug.call_args[0][0],
                             "'bad' is not a valid target environment, defaulting to 'production'.")

    def test_determine_artifact_location_filter_missing_parts(self):
        config = DecisioningConfig(None, None, environment=ENVIRONMENT_DEV)
        artifact_location = determine_artifact_location(config)
        self.assertEqual(artifact_location, "https://assets.adobetarget.com/development/v1/rules.json")
