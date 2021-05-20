# coding: utf-8

"""
    Adobe Target Delivery API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class View(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'name': 'str',
        'key': 'str',
        'options': 'list[Option]',
        'metrics': 'list[Metric]',
        'analytics': 'AnalyticsResponse',
        'state': 'str',
        'trace': 'dict(str, object)'
    }

    attribute_map = {
        'name': 'name',
        'key': 'key',
        'options': 'options',
        'metrics': 'metrics',
        'analytics': 'analytics',
        'state': 'state',
        'trace': 'trace'
    }

    def __init__(self, name=None, key=None, options=None, metrics=None, analytics=None, state=None, trace=None):
        """View - a model defined in OpenAPI"""

        self._name = None
        self._key = None
        self._options = None
        self._metrics = None
        self._analytics = None
        self._state = None
        self._trace = None
        self.discriminator = None

        if name is not None:
            self.name = name
        if key is not None:
            self.key = key
        if options is not None:
            self.options = options
        if metrics is not None:
            self.metrics = metrics
        if analytics is not None:
            self.analytics = analytics
        if state is not None:
            self.state = state
        if trace is not None:
            self.trace = trace

    @property
    def name(self):
        """Gets the name of this View.

        View Name - Unique view name. If the activity has a metric with a view with this name it will be matched, providing the Key matches as well or is null and view and metric targeting is matched. 

        :return: The name of this View.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this View.

        View Name - Unique view name. If the activity has a metric with a view with this name it will be matched, providing the Key matches as well or is null and view and metric targeting is matched. 

        :param name: The name of this View.
        :type: str
        """
        if name is not None and len(name) > 128:
            raise ValueError("Invalid value for `name`, length must be less than or equal to `128`")

        self._name = name

    @property
    def key(self):
        """Gets the key of this View.

        View Key - An optional encoded String identifier used in advanced scenarios, such as View fingerprinting. Same matching conditions as for View Name. 

        :return: The key of this View.
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this View.

        View Key - An optional encoded String identifier used in advanced scenarios, such as View fingerprinting. Same matching conditions as for View Name. 

        :param key: The key of this View.
        :type: str
        """
        if key is not None and len(key) > 512:
            raise ValueError("Invalid value for `key`, length must be less than or equal to `512`")

        self._key = key

    @property
    def options(self):
        """Gets the options of this View.

        The prefetched content (options) to be displayed for the current view. 

        :return: The options of this View.
        :rtype: list[Option]
        """
        return self._options

    @options.setter
    def options(self, options):
        """Sets the options of this View.

        The prefetched content (options) to be displayed for the current view. 

        :param options: The options of this View.
        :type: list[Option]
        """

        self._options = options

    @property
    def metrics(self):
        """Gets the metrics of this View.

        Click track metrics for the current view. 

        :return: The metrics of this View.
        :rtype: list[Metric]
        """
        return self._metrics

    @metrics.setter
    def metrics(self, metrics):
        """Sets the metrics of this View.

        Click track metrics for the current view. 

        :param metrics: The metrics of this View.
        :type: list[Metric]
        """

        self._metrics = metrics

    @property
    def analytics(self):
        """Gets the analytics of this View.


        :return: The analytics of this View.
        :rtype: AnalyticsResponse
        """
        return self._analytics

    @analytics.setter
    def analytics(self, analytics):
        """Sets the analytics of this View.


        :param analytics: The analytics of this View.
        :type: AnalyticsResponse
        """

        self._analytics = analytics

    @property
    def state(self):
        """Gets the state of this View.

        View state token that must be sent back with display notification for the view.

        :return: The state of this View.
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this View.

        View state token that must be sent back with display notification for the view.

        :param state: The state of this View.
        :type: str
        """

        self._state = state

    @property
    def trace(self):
        """Gets the trace of this View.

        The object containing all trace data for the request, only present if the trace token was provided in the request. 

        :return: The trace of this View.
        :rtype: dict(str, object)
        """
        return self._trace

    @trace.setter
    def trace(self, trace):
        """Sets the trace of this View.

        The object containing all trace data for the request, only present if the trace token was provided in the request. 

        :param trace: The trace of this View.
        :type: dict(str, object)
        """

        self._trace = trace

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, View):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
