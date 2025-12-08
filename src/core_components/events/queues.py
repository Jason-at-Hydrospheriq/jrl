#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from components.events.base import *


class MainEventQueue(BaseEventQueue):
    """ The EventQueue component manages the queue of game events to be processed. """

    def __init__(self) -> None:
        self._queue: Set[BaseGameEvent] = set()