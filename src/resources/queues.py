#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, Set


class BaseEventQueue:
    _queue: Set # FIFO queue of events

    @property
    def queue(self) -> Set:
        """ Get the current queue of events """
        return self._queue
    
    def enqueue(self, event) -> None:
        """ Add an event to the queue """
        self._queue.add(event)
    
    def dequeue(self):
        """ Remove and return an event from the queue """
        return self._queue.pop()
    
    def is_empty(self) -> bool:
        """ Check if the queue is empty """
        return self._queue == set()
    
    def clear(self) -> None:
        """ Clear the queue """
        self._queue.clear()
