#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from handler_components.game_ai import game_behaviors

if TYPE_CHECKING:
    from store import GameStore

from handler import BaseGameHandler, BaseGameLoop, BaseGameTransformer
from handler_components.behaviors import mob_behaviors
from handler_components.base import BaseGameEvent


class GameLoopHandler(BaseGameHandler):
    """The GameLoopHandler is responsible for tranforming Game Inputs and Player Actions into Game Events
    and sending them to the appropriate Queue."""

    def __init__(self, store: GameStore | None = None) -> None:
        super().__init__(store=store, behaviors=game_behaviors)  # type: ignore


class MobLoopHandler(BaseGameHandler):
    """The MobLoopHandler is responsible for tranforming Game AI Actions into Game Events
    and sending them to the appropriate Queue."""

    def __init__(self, store: GameStore | None = None) -> None:
        super().__init__(store=store, behaviors=mob_behaviors)  # type: ignore