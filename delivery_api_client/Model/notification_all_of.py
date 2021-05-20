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


class NotificationAllOf(object):
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
        'id': 'str',
        'impression_id': 'str',
        'type': 'MetricType',
        'timestamp': 'int',
        'tokens': 'list[str]',
        'mbox': 'NotificationMbox',
        'view': 'NotificationView',
        'page_load': 'NotificationPageLoad'
    }

    attribute_map = {
        'id': 'id',
        'impression_id': 'impressionId',
        'type': 'type',
        'timestamp': 'timestamp',
        'tokens': 'tokens',
        'mbox': 'mbox',
        'view': 'view',
        'page_load': 'pageLoad'
    }

    def __init__(self, id=None, impression_id=None, type=None, timestamp=None, tokens=None, mbox=None, view=None, page_load=None):
        """NotificationAllOf - a model defined in OpenAPI"""

        self._id = None
        self._impression_id = None
        self._type = None
        self._timestamp = None
        self._tokens = None
        self._mbox = None
        self._view = None
        self._page_load = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if impression_id is not None:
            self.impression_id = impression_id
        if type is not None:
            self.type = type
        if timestamp is not None:
            self.timestamp = timestamp
        if tokens is not None:
            self.tokens = tokens
        if mbox is not None:
            self.mbox = mbox
        if view is not None:
            self.view = view
        if page_load is not None:
            self.page_load = page_load

    @property
    def id(self):
        """Gets the id of this NotificationAllOf.

        Notification id will be returned in response and will indicate that the notification was processed successfully. 

        :return: The id of this NotificationAllOf.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this NotificationAllOf.

        Notification id will be returned in response and will indicate that the notification was processed successfully. 

        :param id: The id of this NotificationAllOf.
        :type: str
        """
        if id is not None and len(id) > 200:
            raise ValueError("Invalid value for `id`, length must be less than or equal to `200`")

        self._id = id

    @property
    def impression_id(self):
        """Gets the impression_id of this NotificationAllOf.

        Impression id is used to stitch (link) the current notification with a previous notification or execute request. In case they both of them match, the second and other subsequent requests will not generate a new impression to the activity, experience etc. 

        :return: The impression_id of this NotificationAllOf.
        :rtype: str
        """
        return self._impression_id

    @impression_id.setter
    def impression_id(self, impression_id):
        """Sets the impression_id of this NotificationAllOf.

        Impression id is used to stitch (link) the current notification with a previous notification or execute request. In case they both of them match, the second and other subsequent requests will not generate a new impression to the activity, experience etc. 

        :param impression_id: The impression_id of this NotificationAllOf.
        :type: str
        """
        if impression_id is not None and len(impression_id) > 128:
            raise ValueError("Invalid value for `impression_id`, length must be less than or equal to `128`")

        self._impression_id = impression_id

    @property
    def type(self):
        """Gets the type of this NotificationAllOf.


        :return: The type of this NotificationAllOf.
        :rtype: MetricType
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this NotificationAllOf.


        :param type: The type of this NotificationAllOf.
        :type: MetricType
        """

        self._type = type

    @property
    def timestamp(self):
        """Gets the timestamp of this NotificationAllOf.

        Timestamp of the notification, in milliseconds elapsed since UNIX epoch.

        :return: The timestamp of this NotificationAllOf.
        :rtype: int
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this NotificationAllOf.

        Timestamp of the notification, in milliseconds elapsed since UNIX epoch.

        :param timestamp: The timestamp of this NotificationAllOf.
        :type: int
        """

        self._timestamp = timestamp

    @property
    def tokens(self):
        """Gets the tokens of this NotificationAllOf.

        A list of tokens for displayed content or clicked selectors, based on the type of notification.

        :return: The tokens of this NotificationAllOf.
        :rtype: list[str]
        """
        return self._tokens

    @tokens.setter
    def tokens(self, tokens):
        """Sets the tokens of this NotificationAllOf.

        A list of tokens for displayed content or clicked selectors, based on the type of notification.

        :param tokens: The tokens of this NotificationAllOf.
        :type: list[str]
        """

        self._tokens = tokens

    @property
    def mbox(self):
        """Gets the mbox of this NotificationAllOf.


        :return: The mbox of this NotificationAllOf.
        :rtype: NotificationMbox
        """
        return self._mbox

    @mbox.setter
    def mbox(self, mbox):
        """Sets the mbox of this NotificationAllOf.


        :param mbox: The mbox of this NotificationAllOf.
        :type: NotificationMbox
        """

        self._mbox = mbox

    @property
    def view(self):
        """Gets the view of this NotificationAllOf.


        :return: The view of this NotificationAllOf.
        :rtype: NotificationView
        """
        return self._view

    @view.setter
    def view(self, view):
        """Sets the view of this NotificationAllOf.


        :param view: The view of this NotificationAllOf.
        :type: NotificationView
        """

        self._view = view

    @property
    def page_load(self):
        """Gets the page_load of this NotificationAllOf.


        :return: The page_load of this NotificationAllOf.
        :rtype: NotificationPageLoad
        """
        return self._page_load

    @page_load.setter
    def page_load(self, page_load):
        """Sets the page_load of this NotificationAllOf.


        :param page_load: The page_load of this NotificationAllOf.
        :type: NotificationPageLoad
        """

        self._page_load = page_load

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
        if not isinstance(other, NotificationAllOf):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
