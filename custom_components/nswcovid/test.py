#!/usr/bin/env python3
import logging
import asyncio

from nswcovid import NSWCovid

logging.basicConfig(level=logging.DEBUG)

_logger = logging.getLogger(__name__)

LOOP = asyncio.get_event_loop()
COVID = NSWCovid(loop=LOOP)


def event_receiver(event_type=None, statistic_id=None, statistic=None, ts=None):
    _logger.debug(event_type)
    _logger.debug(statistic_id)
    _logger.debug(statistic)
    _logger.debug(ts)


async def get_data():
    await COVID.refresh()
    COVID.track(event_receiver=event_receiver)


LOOP.run_until_complete(get_data())