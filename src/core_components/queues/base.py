#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from email.mime import message
from turtle import clone
from typing import Protocol, Set

from core_components.events.library import BaseGameEvent, GameOver, GameStart, MapUpdate

GAME_OVER = GameOver(message="Game Over! Thanks for playing.")
GAME_START = GameStart(message="Welcome to the Game! Let the adventure begin.")
MAP_UPDATE = MapUpdate(element_name="main_map", message="Map Updated.")

class BaseEventQueue(Protocol):
    __slots__ = ("_queue",)
    _queue: Set[BaseGameEvent] # FIFO queue of events

    @property
    def queue(self) -> Set:
        """ Get the current queue of events """
        return self._queue
    
    def post(self, event: BaseGameEvent, message: str | None = None) -> None:
        """ Add an event to the queue """
        clone = deepcopy(event)
        if message:
            clone.message = message   
        self._queue.add(clone)
    
    def get(self):
        """ Remove and return an event from the queue """
        return self._queue.pop()
    
    def is_empty(self) -> bool:
        """ Check if the queue is empty """
        return self._queue == set()
    
    def clear(self) -> None:
        """ Clear the queue """
        self._queue.clear()
