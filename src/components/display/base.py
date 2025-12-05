#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol, TYPE_CHECKING
from tcod.console import Console

if TYPE_CHECKING:
    from engine import Engine

class BaseUIComponent(Protocol):

    def render(self, console: Console, engine: Engine) -> None:
        """ Render the UI component """
        raise NotImplementedError()