#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Protocol
import numpy as np

from actions import Action, MeleeAction, MoveAction, NoAction

if TYPE_CHECKING:
    from entities import AICharactor, Charactor
    from game_map import MapCoords

class AIEvent(Protocol):

    def to_action(self) -> Action:
        ...


class AIEventNone:
    def __init__(self, entity: AICharactor) -> None:
        self.entity = entity
        self.target = None
        self.location = None
    
    def to_action(self) -> Action:
        return NoAction(self.entity)

class AIEventPathToTarget:
    def __init__(self, entity: AICharactor, location: MapCoords) -> None:
        self.entity = entity
        self.target = None
        self.location = location

    def to_action(self) -> Action:
        return MoveAction(self.entity, self.location)
    
class AIEventTargetInMeleeRange:
    def __init__(self, entity: AICharactor, target: Charactor) -> None:
        self.entity = entity
        self.target = target
        self.location = None

    def to_action(self) -> Action:
        return MeleeAction(self.entity, self.target)
        