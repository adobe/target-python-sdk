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


class Trace(object):
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
        'authorization_token': 'str',
        'usage': 'dict(str, str)'
    }

    attribute_map = {
        'authorization_token': 'authorizationToken',
        'usage': 'usage'
    }

    def __init__(self, authorization_token=None, usage=None):
        """Trace - a model defined in OpenAPI"""

        self._authorization_token = None
        self._usage = None
        self.discriminator = None

        self.authorization_token = authorization_token
        if usage is not None:
            self.usage = usage

    @property
    def authorization_token(self):
        """Gets the authorization_token of this Trace.


        :return: The authorization_token of this Trace.
        :rtype: str
        """
        return self._authorization_token

    @authorization_token.setter
    def authorization_token(self, authorization_token):
        """Sets the authorization_token of this Trace.


        :param authorization_token: The authorization_token of this Trace.
        :type: str
        """
        if authorization_token is None:
            raise ValueError("Invalid value for `authorization_token`, must not be `None`")

        self._authorization_token = authorization_token

    @property
    def usage(self):
        """Gets the usage of this Trace.

        A String dictionary of client SDK usage tracking and internal diagnostics metadata. 

        :return: The usage of this Trace.
        :rtype: dict(str, str)
        """
        return self._usage

    @usage.setter
    def usage(self, usage):
        """Sets the usage of this Trace.

        A String dictionary of client SDK usage tracking and internal diagnostics metadata. 

        :param usage: The usage of this Trace.
        :type: dict(str, str)
        """

        self._usage = usage

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
        if not isinstance(other, Trace):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
