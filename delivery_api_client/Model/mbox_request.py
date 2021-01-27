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


class MboxRequest(object):
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
        'address': 'Address',
        'parameters': 'dict(str, str)',
        'profile_parameters': 'dict(str, str)',
        'order': 'Order',
        'product': 'Product',
        'index': 'int',
        'name': 'str'
    }

    attribute_map = {
        'address': 'address',
        'parameters': 'parameters',
        'profile_parameters': 'profileParameters',
        'order': 'order',
        'product': 'product',
        'index': 'index',
        'name': 'name'
    }

    def __init__(self, address=None, parameters=None, profile_parameters=None, order=None, product=None, index=None, name=None):  # noqa: E501
        """MboxRequest - a model defined in OpenAPI"""  # noqa: E501

        self._address = None
        self._parameters = None
        self._profile_parameters = None
        self._order = None
        self._product = None
        self._index = None
        self._name = None
        self.discriminator = None

        if address is not None:
            self.address = address
        if parameters is not None:
            self.parameters = parameters
        if profile_parameters is not None:
            self.profile_parameters = profile_parameters
        if order is not None:
            self.order = order
        if product is not None:
            self.product = product
        if index is not None:
            self.index = index
        if name is not None:
            self.name = name

    @property
    def address(self):
        """Gets the address of this MboxRequest.  # noqa: E501


        :return: The address of this MboxRequest.  # noqa: E501
        :rtype: Address
        """
        return self._address

    @address.setter
    def address(self, address):
        """Sets the address of this MboxRequest.


        :param address: The address of this MboxRequest.  # noqa: E501
        :type: Address
        """

        self._address = address

    @property
    def parameters(self):
        """Gets the parameters of this MboxRequest.  # noqa: E501

        Parameters map. Same object is reused for mbox or profile parameters with slight validation differences. Following names are not allowed for mbox parameters: 'orderId', 'orderTotal', productPurchasedIds' Validation (for both mbox and profile parameters):   * Max 50 parameters limit.   * Parameter name should not be blank.   * Parameter name max length 128.   * Parameter name should not start with 'profile.'   * Parameter value length max 5000.   # noqa: E501

        :return: The parameters of this MboxRequest.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Sets the parameters of this MboxRequest.

        Parameters map. Same object is reused for mbox or profile parameters with slight validation differences. Following names are not allowed for mbox parameters: 'orderId', 'orderTotal', productPurchasedIds' Validation (for both mbox and profile parameters):   * Max 50 parameters limit.   * Parameter name should not be blank.   * Parameter name max length 128.   * Parameter name should not start with 'profile.'   * Parameter value length max 5000.   # noqa: E501

        :param parameters: The parameters of this MboxRequest.  # noqa: E501
        :type: dict(str, str)
        """

        self._parameters = parameters

    @property
    def profile_parameters(self):
        """Gets the profile_parameters of this MboxRequest.  # noqa: E501

        Parameters map. Same object is reused for mbox or profile parameters with slight validation differences. Following names are not allowed for mbox parameters: 'orderId', 'orderTotal', productPurchasedIds' Validation (for both mbox and profile parameters):   * Max 50 parameters limit.   * Parameter name should not be blank.   * Parameter name max length 128.   * Parameter name should not start with 'profile.'   * Parameter value length max 5000.   # noqa: E501

        :return: The profile_parameters of this MboxRequest.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._profile_parameters

    @profile_parameters.setter
    def profile_parameters(self, profile_parameters):
        """Sets the profile_parameters of this MboxRequest.

        Parameters map. Same object is reused for mbox or profile parameters with slight validation differences. Following names are not allowed for mbox parameters: 'orderId', 'orderTotal', productPurchasedIds' Validation (for both mbox and profile parameters):   * Max 50 parameters limit.   * Parameter name should not be blank.   * Parameter name max length 128.   * Parameter name should not start with 'profile.'   * Parameter value length max 5000.   # noqa: E501

        :param profile_parameters: The profile_parameters of this MboxRequest.  # noqa: E501
        :type: dict(str, str)
        """

        self._profile_parameters = profile_parameters

    @property
    def order(self):
        """Gets the order of this MboxRequest.  # noqa: E501


        :return: The order of this MboxRequest.  # noqa: E501
        :rtype: Order
        """
        return self._order

    @order.setter
    def order(self, order):
        """Sets the order of this MboxRequest.


        :param order: The order of this MboxRequest.  # noqa: E501
        :type: Order
        """

        self._order = order

    @property
    def product(self):
        """Gets the product of this MboxRequest.  # noqa: E501


        :return: The product of this MboxRequest.  # noqa: E501
        :rtype: Product
        """
        return self._product

    @product.setter
    def product(self, product):
        """Sets the product of this MboxRequest.


        :param product: The product of this MboxRequest.  # noqa: E501
        :type: Product
        """

        self._product = product

    @property
    def index(self):
        """Gets the index of this MboxRequest.  # noqa: E501

        An index for the mboxes to be executed or prefetched. Mbox index is used for correlation between the mbox request with the mbox response, for either prefetch or execute responses. Index should be unique in the mbox list.   # noqa: E501

        :return: The index of this MboxRequest.  # noqa: E501
        :rtype: int
        """
        return self._index

    @index.setter
    def index(self, index):
        """Sets the index of this MboxRequest.

        An index for the mboxes to be executed or prefetched. Mbox index is used for correlation between the mbox request with the mbox response, for either prefetch or execute responses. Index should be unique in the mbox list.   # noqa: E501

        :param index: The index of this MboxRequest.  # noqa: E501
        :type: int
        """

        self._index = index

    @property
    def name(self):
        """Gets the name of this MboxRequest.  # noqa: E501

        The name of the regional mbox to be evaluated.   # noqa: E501

        :return: The name of this MboxRequest.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this MboxRequest.

        The name of the regional mbox to be evaluated.   # noqa: E501

        :param name: The name of this MboxRequest.  # noqa: E501
        :type: str
        """

        self._name = name

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
        if not isinstance(other, MboxRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other