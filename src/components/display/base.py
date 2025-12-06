#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol, TYPE_CHECKING
from tcod.console import Console

if TYPE_CHECKING:
    from engine import Engine

class BaseUIComponent(Protocol):
    name: str
    upper_Left_x: int
    upper_Left_y: int
    lower_Right_x: int
    lower_Right_y: int
    width: int
    height: int
    console: Console

    def __init__(self, name: str, x: int, y: int, width: int, height: int, console: Console | None = None):
        self.name = name
        self.upper_Left_x = x
        self.upper_Left_y = y
        self.lower_Right_x = x + width
        self.lower_Right_y = y + height
        self.width = width
        self.height = height

        if console:
            self.console = console

    def render(self, engine: Engine) -> None:
        """ Render the UI component """
        raise NotImplementedError()