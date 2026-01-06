#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import tcod
from transitions import Machine

from core_components.loops.custom_types import StateActionObject

if TYPE_CHECKING:
    from core_components.store import GameStore

from core_components.loops.behaviors import game_behaviors, mob_behaviors
from core_components.loops.base import BaseGameHandler, BaseGameLoop, BaseGameTransformer, BaseGameEvent


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