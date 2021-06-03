# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""On Device Decisioning util functions"""
# pylint: disable=protected-access
import requests
from tld import get_tld
from target_decisioning_engine.constants import CDN_BASE
from target_decisioning_engine.constants import ARTIFACT_FILENAME
from target_decisioning_engine.constants import SUPPORTED_ARTIFACT_MAJOR_VERSION
from target_decisioning_engine.messages import MESSAGES
from target_tools.constants import POSSIBLE_ENVIRONMENTS
from target_tools.constants import EMPTY_STRING
from target_tools.constants import ENVIRONMENT_PROD
from target_tools.logger import get_logger
from target_tools.utils import get_mbox_names
from target_tools.utils import get_view_names
from target_tools.utils import has_requested_views
from target_tools.utils import is_string
from target_tools.utils import parse_int


logger = get_logger()

DEFAULT_PARSED_URL = {
    "path": "",
    "query": "",
    "fragment": "",
    "domain": "",
    "subdomain": "",
    "topLevelDomain": ""
}


def get_rule_key(rule):
    """
    :param rule: (target_decisioning_engine.types.decisioning_artifact.Rule) Decisioning artifact rule, required
    :return: (str) rule key
    """
    return rule.get("ruleKey")


def _get_default_parsed_url(url):
    """Returns default dict for urls that cannot be parsed"""
    parsed = dict(DEFAULT_PARSED_URL)
    parsed["url"] = url
    return parsed


def parse_url(url):
    """parse url"""
    if not is_string(url):
        return _get_default_parsed_url(EMPTY_STRING)

    parsed = get_tld(url, as_object=True, fail_silently=True)
    if not parsed:
        return _get_default_parsed_url(url)

    path, query, fragment = [getattr(parsed.parsed_url, key, "") for key in ["path", "query", "fragment"]]

    return {
        "url": url,
        "path": path,
        "query": query,
        "fragment": fragment,
        "domain": parsed.domain,
        "subdomain": parsed.subdomain,
        "topLevelDomain": parsed.tld
    }


def has_remote_dependency(artifact, request):
    """
    :param artifact: (target_decisioning_engine.types.decisioning_artifact.DecisioningArtifact)
    Decisioning artifact, required
    :param request: (delivery_api_client.Model.delivery_request.DeliveryRequest)
            Target Delivery API request, required
    :return: (dict) items with remote dependencies
    """
    if not artifact:
        raise Exception(MESSAGES.get("ARTIFACT_NOT_AVAILABLE"))

    requested_mboxes = get_mbox_names(request)
    requested_views = get_view_names(request)

    remote_mboxes, local_mboxes, remote_views, local_views = \
        [artifact.get(k, []) for k in ("remoteMboxes", "localMboxes", "remoteViews", "localViews")]

    mboxes_that_require_remote = set()
    for mbox_name in remote_mboxes:
        if mbox_name in requested_mboxes:
            mboxes_that_require_remote.add(mbox_name)
    for mbox_name in requested_mboxes:
        if mbox_name not in local_mboxes:
            mboxes_that_require_remote.add(mbox_name)

    if has_requested_views(request) and not requested_views:
        views_that_require_remote = set(remote_views)
    else:
        views_that_require_remote = set()
        for view_name in remote_views:
            if view_name in requested_views:
                views_that_require_remote.add(view_name)
        for view_name in requested_views:
            if view_name not in local_views:
                views_that_require_remote.add(view_name)

    return {
        "remote_needed": bool(mboxes_that_require_remote or views_that_require_remote),
        "remote_mboxes": list(mboxes_that_require_remote),
        "remote_views": list(views_that_require_remote)
    }


def match_major_version(semantic_version, major_version):
    """
    :param semantic_version: (str)
    :param major_version: (int)
    """
    parts = semantic_version.split(".")
    major = parse_int(parts[0])
    return major_version == major


def get_valid_environment(environment_name):
    """
    :param environment_name: (str) Environment name
    """
    is_valid = environment_name in POSSIBLE_ENVIRONMENTS
    if not is_valid:
        logger.debug(MESSAGES.get("INVALID_ENVIRONMENT")(environment_name, ENVIRONMENT_PROD))

    return environment_name if is_valid else ENVIRONMENT_PROD


def get_target_environment(config):
    """
    :param config: (target_decisioning_engine.types.decisioning_config.DecisioningConfig) config
    """
    environment = config.environment or ENVIRONMENT_PROD
    return get_valid_environment(environment)


def get_cdn_environment(config):
    """
    :param config: (target_decisioning_engine.types.decisioning_config.DecisioningConfig) config
    """
    cdn_environment = config.cdn_environment or ENVIRONMENT_PROD
    return get_valid_environment(cdn_environment)


def get_cdn_base_path(config):
    """
    :param config: (target_decisioning_engine.types.decisioning_config.DecisioningConfig) config
    """
    cdn_base_path = config.cdn_base_path

    if not cdn_base_path:
        cdn_environment = get_cdn_environment(config)
        env = cdn_environment if cdn_environment in POSSIBLE_ENVIRONMENTS else ENVIRONMENT_PROD
        cdn_base_path = CDN_BASE[env]

    return "https://{}".format(cdn_base_path)


def get_geo_lookup_path(config):
    """
    :param config: (target_decisioning_engine.types.decisioning_config.DecisioningConfig) config
    """
    cdn_base_path = get_cdn_base_path(config)
    return "{}/v{}/geo".format(cdn_base_path, SUPPORTED_ARTIFACT_MAJOR_VERSION)


def determine_artifact_location(config):
    """
    :param config: (target_decisioning_engine.types.decisioning_config.DecisioningConfig) config
    """
    target_environment = get_target_environment(config)

    location_parts = [
        get_cdn_base_path(config),
        config.client,
        target_environment,
        "v{}".format(SUPPORTED_ARTIFACT_MAJOR_VERSION),
        ARTIFACT_FILENAME
    ]
    filtered = filter(None, location_parts)
    return "/".join(filtered)


def should_retry_http_code(status_code):
    """
    :param status_code: (int) http status code to check for retry eligibility
    :return: (bool) whether or not responses with the status_code should be retried
    """
    return status_code not in range(200, 500)


def get_http_codes_to_retry():
    """
    :return: set of http codes that should be retried
    """
    return set(x for x in requests.status_codes._codes if should_retry_http_code(x))
