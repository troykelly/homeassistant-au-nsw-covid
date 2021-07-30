# -*- coding: utf-8 -*-
"""
Protocol handler for NSW Covid
"""

import asyncio
import logging
from datetime import datetime, timedelta
import json
import hashlib
import requests
import backoff


from ..exceptions import (
    NSWCovidAPIError,
    NSWCovidAccessDenied,
)

_logger = logging.getLogger(__name__)
logging.getLogger("backoff").addHandler(logging.StreamHandler())


def fatal_code(e):
    return 400 <= e.response.status_code < 500


@backoff.on_exception(
    backoff.expo, requests.exceptions.RequestException, max_time=300, giveup=fatal_code
)
class Protocol(object):
    def __init__(
        self,
        host="www.health.nsw.gov.au",
        port=443,
        protocol="https",
        path="Infectious/covid-19/Pages/stats-nsw.aspx",
        expiryms=60000,
        loop=None,
    ):
        super().__init__()

        self.__session = requests.Session()

        self.__loop = loop if loop else asyncio.get_event_loop()

        self.__host = host
        self.__port = port
        self.__protocol = protocol
        self.__path = path
        self.__expiryms = int(expiryms)
        self.__cache_data = {}

        self.__api_url = (
            f"{self.__protocol}://{self.__host}:{self.__port}/{self.__path}"
        )

        _logger.debug("Protocol handler ready.")

    @property
    def loop(self):
        if not self.__loop:
            return None
        return self.__loop

    def __request(
        self, method="GET", url=None, params=None, json_data=None, headers=None
    ):

        _logger.debug(
            {
                "url": url,
                "params": params,
                "data": json_data,
                "headers": headers,
            }
        )

        try:
            response = self.__session.request(
                method, url, params=params, json=json_data, headers=headers
            )
        except Exception as err:
            _logger.error("No response at all")
            _logger.exception(err)

        status_code = getattr(response, "status_code", None)
        body = getattr(response, "text", None)

        if not status_code:
            raise NSWCovidAPIError("NSW Covid API failed to repond.", response=response)

        success = 200 <= response.status_code <= 299

        if response.status_code == 401 or response.status_code == 403:
            raise NSWCovidAccessDenied(
                "NSWCovid API Access Denied",
                status_code=response.status_code,
                body=body,
                headers=response.headers,
                response=response,
            )

        if not success:
            raise NSWCovidAPIError(
                "NSWCovid API Error",
                status_code=response.status_code,
                body=body,
                headers=response.headers,
                response=response,
            )

        return body

    async def api(
        self,
        method="GET",
        host=None,
        path=None,
        data=None,
        headers={},
        query_string={},
    ):
        """Make a request to the NSWCovid API

        Attributes:
            method (str): The request verb ie GET PUT POST DELETE
            path (str): The path of the API endpoint
            data (object): Data to be passed as a querystring
            headers (object): Any headers to be sent
            no_check (bool): Don't check for an expired token
            use_internal_api (bool): Use the alternate internal API endpoint
        """

        request_host = (
            f"{self.__protocol}://{self.__host}:{self.__port}" if not host else host
        )

        url = f"{request_host}/{self.__path}" if not path else f"{request_host}/{path}"

        method = method.upper()
        json_data = None
        params = None

        if method == "GET":
            if data and not query_string:
                params = data
            elif query_string:
                params = query_string
        elif method == "POST":
            if data:
                json_data = data
            if query_string:
                params = query_string
        elif method == "DELETE":
            if data:
                json_data = data
            if query_string:
                params = query_string
        elif method == "PUT":
            if data:
                json_data = data
            if query_string:
                params = query_string

        body = None

        def process_request(method, url, params, jsonRequestData, headers):
            return self.__request(
                method=method,
                url=url,
                params=params,
                json_data=jsonRequestData,
                headers=headers,
            )

        if method == "GET":
            cache = self.__cache(url=url, query_string=params)
            if cache:
                return cache

        try:
            body = await self.__loop.run_in_executor(
                None, process_request, method, url, params, json_data, headers
            )
        except NSWCovidAccessDenied as err:
            raise NSWCovidAccessDenied(
                "NSWCovid API Access Denied",
                status_code=err.status_code,
                body=err.body,
                json=err.json,
                headers=err.headers,
                response=err.response,
            )

        if method == "GET":
            self.__cache(url=url, query_string=params, body=body)

        return {
            "retrieved": datetime.now(),
            "expires": datetime.now() + timedelta(milliseconds=self.__expiryms),
            "body": body,
        }

    async def api_get(self, path=None, data=None, host=None):
        """Make a get request to the NSWCovid API

        Attributes:
            path (str): The path of the API endpoint
            data (object): Data to be passed as a querystring
        """
        return await self.api("GET", path=path, data=data, host=host)

    async def api_post(self, path=None, data=None, query_string=None, host=None):
        """Make a post request to the NSWCovid API

        Attributes:
            path (str): The path of the API endpoint
            data (object): Data to be passed as a json payload
        """
        return await self.api(
            "POST", path=path, data=data, query_string=query_string, host=host
        )

    async def api_delete(self, path=None, data=None, query_string=None, host=None):
        """Make a delete request to the NSWCovid API

        Attributes:
            path (str): The path of the API endpoint
            data (object): Data to be passed as a json payload
        """
        return await self.api(
            "DELETE", path=path, data=data, query_string=query_string, host=host
        )

    async def api_put(self, path=None, data=None, query_string=None, host=None):
        """Make a put request to the NSWCovid API

        Attributes:
            path (str): The path of the API endpoint
            data (object): Data to be passed as a json payload
        """
        return await self.api(
            "PUT", path=path, data=data, query_string=query_string, host=host
        )

    def __cache(self, url=None, query_string=None, body=None):
        """Handle caching of GET queries

        Attributes:
            url (str): The url to be cached
            query_string (str): The query string to be cached
        """

        if not url:
            url = ""

        if not query_string:
            query_string = {}

        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        query_string_hash = hashlib.md5(
            json.dumps(query_string, sort_keys=True).encode("utf-8")
        ).hexdigest()

        cache_key = f"{url_hash}_{query_string_hash}"

        if body:
            self.__cache_data[cache_key] = {
                "retrieved": datetime.now(),
                "expires": datetime.now() + timedelta(milliseconds=self.__expiryms),
                "body": body,
            }
            return self.__cache_data[cache_key]

        if cache_key in self.__cache_data:
            cache = self.__cache_data[cache_key]
            now = datetime.now()
            if now < cache["expires"]:
                return cache

        return None
