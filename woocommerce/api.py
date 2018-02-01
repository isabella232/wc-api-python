# -*- coding: utf-8 -*-

"""
WooCommerce API Class
"""

__title__ = "woocommerce-api"
__version__ = "1.2.1"
__author__ = "Claudio Sanches @ WooThemes"
__license__ = "MIT"

from requests import request
from json import dumps as jsonencode
from woocommerce.oauth import OAuth


class API(object):
    """ API Class """

    def __init__(self, url, consumer_key, consumer_secret, **kwargs):
        self.url = url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.wp_api = kwargs.get("wp_api", False)
        self.version = kwargs.get("version", "v3")
        self.is_ssl = self.__is_ssl()
        self.timeout = kwargs.get("timeout", 5)
        self.verify_ssl = kwargs.get("verify_ssl", True)
        self.query_string_auth = kwargs.get("query_string_auth", False)

    def __is_ssl(self):
        """ Check if url use HTTPS """
        return self.url.startswith("https")

    def __get_url(self, endpoint):
        """ Get URL for requests """
        url = self.url
        api = "wc-api"

        if url.endswith("/") is False:
            url = "%s/" % url

        if self.wp_api:
            api = "wp-json"

        return "%s%s/%s/%s" % (url, api, self.version, endpoint)

    def __get_oauth_url(self, url, method):
        """ Generate oAuth1.0a URL """
        oauth = OAuth(
            url=url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version=self.version,
            method=method
        )

        return oauth.get_oauth_url()

    def __request(self, method, endpoint, data, params=None, **kwargs):
        """ Do requests """
        if params is None:
            params = {}
        url = self.__get_url(endpoint)
        auth = None
        headers = {
            "user-agent": "WooCommerce API Client-Python/%s" % __version__,
            "accept": "application/json"
        }

        if self.is_ssl is True and self.query_string_auth is False:
            auth = (self.consumer_key, self.consumer_secret)
        elif self.is_ssl is True and self.query_string_auth is True:
            params.update({
                "consumer_key": self.consumer_key,
                "consumer_secret": self.consumer_secret
            })
        else:
            url = self.__get_oauth_url(url, method)

        if data is not None:
            data = jsonencode(data, ensure_ascii=False).encode('utf-8')
            headers["content-type"] = "application/json;charset=utf-8"

        return request(
            method=method,
            url=url,
            verify=self.verify_ssl,
            auth=auth,
            params=params,
            data=data,
            timeout=self.timeout,
            headers=headers,
            **kwargs
        )

    def get(self, endpoint, **kwargs):
        """ Get requests """
        return self.__request("GET", endpoint, None, **kwargs)

    def post(self, endpoint, data, **kwargs):
        """ POST requests """
        return self.__request("POST", endpoint, data, **kwargs)

    def put(self, endpoint, data, **kwargs):
        """ PUT requests """
        return self.__request("PUT", endpoint, data, **kwargs)

    def delete(self, endpoint, **kwargs):
        """ DELETE requests """
        return self.__request("DELETE", endpoint, None, **kwargs)

    def options(self, endpoint, **kwargs):
        """ OPTIONS requests """
        return self.__request("OPTIONS", endpoint, None, **kwargs)
