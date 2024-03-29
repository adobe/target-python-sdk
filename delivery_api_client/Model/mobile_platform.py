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


class MobilePlatform(object):
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
        'device_name': 'str',
        'device_type': 'DeviceType',
        'platform_type': 'MobilePlatformType',
        'version': 'str'
    }

    attribute_map = {
        'device_name': 'deviceName',
        'device_type': 'deviceType',
        'platform_type': 'platformType',
        'version': 'version'
    }

    def __init__(self, device_name=None, device_type=None, platform_type=None, version=None):
        """MobilePlatform - a model defined in OpenAPI"""

        self._device_name = None
        self._device_type = None
        self._platform_type = None
        self._version = None
        self.discriminator = None

        if device_name is not None:
            self.device_name = device_name
        self.device_type = device_type
        self.platform_type = platform_type
        if version is not None:
            self.version = version

    @property
    def device_name(self):
        """Gets the device_name of this MobilePlatform.

        Optional field, added to help with device detection using device atlas. This is equivalent of a.DeviceName field passed in from Mobile SDK 

        :return: The device_name of this MobilePlatform.
        :rtype: str
        """
        return self._device_name

    @device_name.setter
    def device_name(self, device_name):
        """Sets the device_name of this MobilePlatform.

        Optional field, added to help with device detection using device atlas. This is equivalent of a.DeviceName field passed in from Mobile SDK 

        :param device_name: The device_name of this MobilePlatform.
        :type: str
        """

        self._device_name = device_name

    @property
    def device_type(self):
        """Gets the device_type of this MobilePlatform.


        :return: The device_type of this MobilePlatform.
        :rtype: DeviceType
        """
        return self._device_type

    @device_type.setter
    def device_type(self, device_type):
        """Sets the device_type of this MobilePlatform.


        :param device_type: The device_type of this MobilePlatform.
        :type: DeviceType
        """
        if device_type is None:
            raise ValueError("Invalid value for `device_type`, must not be `None`")

        self._device_type = device_type

    @property
    def platform_type(self):
        """Gets the platform_type of this MobilePlatform.


        :return: The platform_type of this MobilePlatform.
        :rtype: MobilePlatformType
        """
        return self._platform_type

    @platform_type.setter
    def platform_type(self, platform_type):
        """Sets the platform_type of this MobilePlatform.


        :param platform_type: The platform_type of this MobilePlatform.
        :type: MobilePlatformType
        """
        if platform_type is None:
            raise ValueError("Invalid value for `platform_type`, must not be `None`")

        self._platform_type = platform_type

    @property
    def version(self):
        """Gets the version of this MobilePlatform.

        If not specified - all activities with any platformVersion will be evaluated. If specified - only activities with the same platformVersion will be evaluated. 

        :return: The version of this MobilePlatform.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this MobilePlatform.

        If not specified - all activities with any platformVersion will be evaluated. If specified - only activities with the same platformVersion will be evaluated. 

        :param version: The version of this MobilePlatform.
        :type: str
        """
        if version is not None and len(version) > 128:
            raise ValueError("Invalid value for `version`, length must be less than or equal to `128`")

        self._version = version

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
        if not isinstance(other, MobilePlatform):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
