# -*- coding: utf-8 -*-
"""
Statistic handler for NSWCovid
"""

import logging
from datetime import datetime, timedelta
import asyncio
import re
import json
import pytz
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)

TZ = pytz.timezone("Australia/Sydney")
ATTRIBUTION = "Health Protection NSW https://www.health.nsw.gov.au/Infectious/covid-19/Pages/stats-nsw.aspx#"
DATA_SOURCES = {
    "published": {
        "host": None,
        "path": None,
        "name": "Published",
        "type": "nswcoviddate",
        "unit": "date",
        "selector": "#maincontent > nav > h1",
        "regex": "\d+[ap]m\s+\d+\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+(?:20)?\d\d",
    },
    "locally_active": {
        "host": None,
        "path": None,
        "name": "Locally Active",
        "type": "integer",
        "unit": "case",
        "selector": "#ContentHtml1Zone2 > div:nth-child(1) > div > div.active-cases.calloutbox > ul > li:nth-child(1) > span",
    },
    "interstate_active": {
        "host": None,
        "path": None,
        "name": "Interstate Active",
        "type": "integer",
        "unit": "case",
        "selector": "#ContentHtml1Zone2 > div:nth-child(1) > div > div.active-cases.calloutbox > ul > li:nth-child(2) > span",
    },
    "overseas_active": {
        "host": None,
        "path": None,
        "name": "Overseas Active",
        "type": "integer",
        "unit": "case",
        "selector": "#ContentHtml1Zone2 > div:nth-child(1) > div > div.active-cases.calloutbox > ul > li:nth-child(3) > span",
    },
    "last_24_hours_known": {
        "host": None,
        "path": None,
        "name": "Last 24 Hours Known Source",
        "type": "integer",
        "unit": "case",
        "selector": "#known > ul > li:nth-child(1) > span.number",
    },
    "last_24_hours_unknown": {
        "host": None,
        "path": None,
        "name": "Last 24 Hours Unknown Source",
        "type": "integer",
        "unit": "case",
        "selector": "#unknown > ul > li:nth-child(1) > span.number",
    },
    "last_24_hours_interstate": {
        "host": None,
        "path": None,
        "name": "Last 24 Hours Interstate Source",
        "type": "integer",
        "unit": "case",
        "selector": "#interstate > ul > li:nth-child(1) > span.number",
    },
    "last_24_hours_overseas": {
        "host": None,
        "path": None,
        "name": "Last 24 Hours Overseas Source",
        "type": "integer",
        "unit": "case",
        "selector": "#overseas > ul > li:nth-child(1) > span.number",
    },
    "last_24_hours_total": {
        "host": None,
        "path": None,
        "name": "Last 24 Hours Total",
        "type": "integer",
        "unit": "case",
        "selector": "#case > ul > li:nth-child(1) > span.number",
    },
    "last_24_hours_tests": {
        "host": None,
        "path": None,
        "name": "Last 24 Hours Tests",
        "type": "integer",
        "unit": "test",
        "selector": "#testing > ul > li:nth-child(1) > span.number",
    },
    "this_week_known": {
        "host": None,
        "path": None,
        "name": "This Week Known Source",
        "type": "integer",
        "unit": "case",
        "selector": "#known > ul > li:nth-child(2) > span.number",
    },
    "this_week_unknown": {
        "host": None,
        "path": None,
        "name": "This Week Unknown Source",
        "type": "integer",
        "unit": "case",
        "selector": "#unknown > ul > li:nth-child(2) > span.number",
    },
    "this_week_interstate": {
        "host": None,
        "path": None,
        "name": "This Week Interstate Source",
        "type": "integer",
        "unit": "case",
        "selector": "#interstate > ul > li:nth-child(2) > span.number",
    },
    "this_week_overseas": {
        "host": None,
        "path": None,
        "name": "This Week Overseas Source",
        "type": "integer",
        "unit": "case",
        "selector": "#overseas > ul > li:nth-child(2) > span.number",
    },
    "this_week_total": {
        "host": None,
        "path": None,
        "name": "This Week Total",
        "type": "integer",
        "unit": "case",
        "selector": "#case > ul > li:nth-child(2) > span.number",
    },
    "this_week_tests": {
        "host": None,
        "path": None,
        "name": "This Week Tests",
        "type": "integer",
        "unit": "test",
        "selector": "#testing > ul > li:nth-child(2) > span.number",
    },
    "last_week_known": {
        "host": None,
        "path": None,
        "name": "Last Week Known Source",
        "type": "integer",
        "unit": "case",
        "selector": "#known > ul > li:nth-child(3) > span.number",
    },
    "last_week_unknown": {
        "host": None,
        "path": None,
        "name": "Last Week Unknown Source",
        "type": "integer",
        "unit": "case",
        "selector": "#unknown > ul > li:nth-child(3) > span.number",
    },
    "last_week_interstate": {
        "host": None,
        "path": None,
        "name": "Last Week Interstate Source",
        "type": "integer",
        "unit": "case",
        "selector": "#interstate > ul > li:nth-child(3) > span.number",
    },
    "last_week_overseas": {
        "host": None,
        "path": None,
        "name": "Last Week Overseas Source",
        "type": "integer",
        "unit": "case",
        "selector": "#overseas > ul > li:nth-child(3) > span.number",
    },
    "last_week_total": {
        "host": None,
        "path": None,
        "name": "Last Week Total",
        "type": "integer",
        "unit": "case",
        "selector": "#case > ul > li:nth-child(3) > span.number",
    },
    "last_week_tests": {
        "host": None,
        "path": None,
        "name": "Last Week Tests",
        "type": "integer",
        "unit": "test",
        "selector": "#testing > ul > li:nth-child(3) > span.number",
    },
    "this_year_known": {
        "host": None,
        "path": None,
        "name": "This Year Known Source",
        "type": "integer",
        "unit": "case",
        "selector": "#known > ul > li:nth-child(4) > span.number",
    },
    "this_year_unknown": {
        "host": None,
        "path": None,
        "name": "This Year Unknown Source",
        "type": "integer",
        "unit": "case",
        "selector": "#unknown > ul > li:nth-child(4) > span.number",
    },
    "this_year_interstate": {
        "host": None,
        "path": None,
        "name": "This Year Interstate Source",
        "type": "integer",
        "unit": "case",
        "selector": "#interstate > ul > li:nth-child(4) > span.number",
    },
    "this_year_overseas": {
        "host": None,
        "path": None,
        "name": "This Year Overseas Source",
        "type": "integer",
        "unit": "case",
        "selector": "#overseas > ul > li:nth-child(4) > span.number",
    },
    "this_year_total": {
        "host": None,
        "path": None,
        "name": "This Year Total",
        "type": "integer",
        "unit": "case",
        "selector": "#case > ul > li:nth-child(4) > span.number",
    },
    "this_year_tests": {
        "host": None,
        "path": None,
        "name": "This Year Tests",
        "type": "integer",
        "unit": "test",
        "selector": "#testing > ul > li:nth-child(4) > span.number",
    },
    "last_24_hours_first_dose": {
        "host": None,
        "path": None,
        "name": "Last 24 Hours First Dose Vaccine",
        "type": "integer",
        "unit": "dose",
        "selector": "#ContentHtml1Zone2 > div:nth-child(3) > div > table > tbody > tr:nth-child(2) > td:nth-child(2)",
    },
    "last_24_hours_second_dose": {
        "host": None,
        "path": None,
        "name": "Last 24 Hours Second Dose Vaccine",
        "type": "integer",
        "unit": "dose",
        "selector": "#ContentHtml1Zone2 > div:nth-child(3) > div > table > tbody > tr:nth-child(3) > td:nth-child(2)",
    },
    "last_24_hours_total_dose": {
        "host": None,
        "path": None,
        "name": "Last 24 Hours Vaccine Total",
        "type": "integer",
        "unit": "dose",
        "selector": "#ContentHtml1Zone2 > div:nth-child(3) > div > table > tbody > tr:nth-child(4) > td:nth-child(2)",
    },
    "total_first_dose": {
        "host": None,
        "path": None,
        "name": "Total First Dose Vaccine",
        "type": "integer",
        "unit": "dose",
        "selector": "#ContentHtml1Zone2 > div:nth-child(3) > div > table > tbody > tr:nth-child(2) > td:nth-child(3)",
    },
    "total_second_dose": {
        "host": None,
        "path": None,
        "name": "Total Second Dose Vaccine",
        "type": "integer",
        "unit": "dose",
        "selector": "#ContentHtml1Zone2 > div:nth-child(3) > div > table > tbody > tr:nth-child(3) > td:nth-child(3)",
    },
    "total_total_dose": {
        "host": None,
        "path": None,
        "name": "Total Vaccine Doses",
        "type": "integer",
        "unit": "dose",
        "selector": "#ContentHtml1Zone2 > div:nth-child(3) > div > table > tbody > tr:nth-child(4) > td:nth-child(3)",
    },
}


class StatisticHandler(object):
    def __init__(self, protocol):
        super().__init__()
        self.__protocol = protocol
        self.__statistics = {}

    @property
    def loop(self):
        if not self.__protocol.loop:
            return None
        return self.__protocol.loop

    @property
    def __list(self):
        if not self.__statistics:
            return []
        return [*self.__statistics]

    @property
    def statistics(self):
        try:
            return self.__statistics
        except AttributeError:
            return None

    async def build(self, limit=20, page=1):
        all_statistics = await self.__listall(limit=limit, page=page)
        while all_statistics:
            for statistic_reference in all_statistics:
                if "id" in statistic_reference:
                    statistic_id = statistic_reference["id"]
                    self.__statistics[statistic_id] = Statistic(
                        handler=self, id=statistic_id, data=statistic_reference
                    )
            page += 1
            all_statistics = await self.__listall(limit=limit, page=page)
        statistic_ids = self.__statistics.keys()
        for id in statistic_ids:
            await self.__statistics[id].refresh()
        return self.__statistics

    async def __listall(self, limit=20, page=1):
        keys = list(DATA_SOURCES.keys())
        pagination = list()
        start = (page - 1) * limit
        end = start + limit
        if end > len(keys):
            end = len(keys)
        if start > end:
            return None
        for i in range(start, end):
            key = keys[i]
            DATA_SOURCES[key]["id"] = key
            pagination.append(DATA_SOURCES[key])
        return pagination

    async def details(self, id):
        """Get device details

        Attributes:
            id (string): The device id
        """
        if not id in self.__statistics:
            return None
        statistic = self.__statistics[id]
        try:
            get = await self.__protocol.api_get(
                host=statistic.host, path=statistic.path
            )
        except:
            return statistic

        if not get:
            _logger.error("No response from server")
            return statistic

        retrieved = None
        if "retrieved" in get:
            retrieved = get["retrieved"]

        if not "body" in get:
            _logger.error("No body from server")
            return statistic

        body = get["body"]

        value = None

        if hasattr(statistic, "selector") and statistic.selector is not None:
            soup = BeautifulSoup(body, features="lxml")
            reference = soup.select_one(statistic.selector)

            if not reference:
                return statistic

            value = reference.string

            if not value:
                return statistic

        if hasattr(statistic, "regex") and statistic.regex is not None:
            match = statistic.regex.search(str(value))
            if not match:
                return statistic

            value = match.group()

            if not value:
                return statistic

        if hasattr(statistic, "typeName") and statistic.typeName is not None:
            if statistic.typeName == "integer":
                value = int(value.replace(",", ""))
            elif statistic.typeName == "float":
                value = float(value.replace(",", ""))
            elif statistic.typeName == "boolean":
                value = bool(value)
            elif statistic.typeName == "string":
                value = str(value)
            elif statistic.typeName == "nswcoviddate":
                value = datetime.strptime(value.upper(), "%I%p %d %B %Y")
                value = value.replace(tzinfo=TZ)
            elif statistic.typeName == "date":
                value = datetime.strptime(value, "%d/%m/%Y")
            elif statistic.typeName == "datetime":
                value = datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
            elif statistic.typeName == "time":
                value = datetime.strptime(value, "%H:%M:%S")
            elif statistic.typeName == "enum":
                value = str(value)
            else:
                value = str(value)

        statistic.status = value
        if retrieved:
            statistic.updated = retrieved
        return statistic

    async def __refresh(self, event_receiver=None):
        await self.__protocol.api_get()
        statistic_ids = self.__statistics.keys()
        for id in statistic_ids:
            self.__protocol.loop.create_task(
                self.__statistics[id].refresh(event_receiver)
            )

    async def __track(self, interval, event_receiver=None):
        while True:
            _logger.debug("track is checking for changes...")
            await self.__refresh(event_receiver)
            await asyncio.sleep(interval.total_seconds())

    def track(self, interval=None, event_receiver=None):
        if not self.__protocol.loop:
            return None

        if not interval:
            interval = timedelta(seconds=60)

        if not isinstance(interval, timedelta):
            interval = timedelta(seconds=interval)

        _logger.debug(
            "Tracking statistics every %d seconds...", interval.total_seconds()
        )

        task = self.__protocol.loop.create_task(
            self.__track(interval=interval, event_receiver=event_receiver)
        )

        return task


class Statistic(object):
    def __init__(self, handler=None, id=None, data=None):
        super().__init__()

        if handler:
            self.__handler = handler

        if id:
            self.__id = id

        if data:
            if "host" in data:
                self.__host = data["host"]
            if "path" in data:
                self.__path = data["path"]
            if "name" in data:
                self.__name = data["name"]
            if "type" in data:
                self.__type = data["type"]
            if "unit" in data:
                self.__unit = data["unit"]
            if "selector" in data:
                self.__selector = data["selector"]
            if "regex" in data:
                self.__regex = data["regex"]
            if "typeId" in data:
                self.__typeId = data["typeId"]
            if "icon" in data:
                self.__icon = data["icon"]
            if "iconId" in data:
                self.__iconId = data["iconId"]

        self.__attribution = ATTRIBUTION
        self.__previous_value = None
        self.__value = None

    def __check_changed(self):
        changed = False
        if not self.__previous_value == self.__value:
            changed = True

        self.__previous_value = self.__value

        return changed

    async def refresh(self, event_receiver=None):
        if not self.__id:
            return
        _logger.debug("Updating statistic %s value", self.__id)
        await self.__handler.details(self.__id)
        if self.changed and event_receiver is not None:
            try:
                event_receiver(
                    event_type="statistic",
                    statistic_id=self.__id,
                    statistic=self,
                    ts=self.updated,
                )
                _logger.debug(
                    "Change sent to event handler for %s (%d)",
                    self.name,
                    self.id,
                )
            except Exception as err:
                _logger.exception(err)

    @property
    def id(self):
        try:
            return self.__id
        except AttributeError:
            return None

    @property
    def changed(self):
        try:
            return self.__changed
        except AttributeError:
            return None

    @property
    def status(self):
        try:
            return self.__value
        except AttributeError:
            return None

    @status.setter
    def status(self, value):
        try:
            self.__value = value
            self.__changed = self.__check_changed()
        except AttributeError:
            pass

    @property
    def attribution(self):
        try:
            return self.__attribution
        except AttributeError:
            return None

    @property
    def updated(self):
        try:
            return self.__retrieved
        except AttributeError:
            return None

    @updated.setter
    def updated(self, value):
        try:
            self.__retrieved = value
        except AttributeError:
            pass

    @property
    def age(self):
        if not self.updated:
            return None

        time_delta = datetime.now() - self.updated
        return round(time_delta.total_seconds())

    @property
    def name(self):
        try:
            return self.__name
        except AttributeError:
            return None

    @property
    def typeName(self):
        try:
            return self.__type
        except AttributeError:
            return None

    @property
    def typeId(self):
        try:
            return self.__typeId
        except AttributeError:
            return None

    @property
    def iconId(self):
        try:
            return self.__iconId
        except AttributeError:
            return None

    @property
    def host(self):
        try:
            return self.__host
        except AttributeError:
            return None

    @property
    def icon(self):
        try:
            return self.__icon
        except AttributeError:
            return None

    @property
    def path(self):
        try:
            return self.__path
        except AttributeError:
            return None

    @property
    def unit(self):
        try:
            return self.__unit
        except AttributeError:
            return None

    @property
    def selector(self):
        try:
            return self.__selector
        except AttributeError:
            return None

    @property
    def regex(self):
        regex = None
        try:
            regex = self.__regex
        except AttributeError:
            return None
        if not regex:
            return None
        return re.compile(regex, re.IGNORECASE)

    @property
    def loop(self):
        try:
            return self.__handler.loop
        except AttributeError:
            return None
