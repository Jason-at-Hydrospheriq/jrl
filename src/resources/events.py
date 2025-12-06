#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Protocol
import numpy as np

from resources.actions import *

if TYPE_CHECKING:
    from entities import AICharactor, Charactor
    from components.game_map import MapCoords


class BaseGameEvent(Protocol):
    message: str


class SystemEvent(BaseGameEvent):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message


class EntityEvent(BaseGameEvent):
    entity: BaseEntity
    message: str

    def __init__(self, entity: BaseEntity, message: str) -> None:
        self.entity = entity
        self.message = message


class UIEvent(BaseGameEvent):
    element_name: str
    message: str

    def __init__(self, element_name: str, message: str) -> None:
        self.element_name = element_name
        self.message = message


class MapUpdate(UIEvent):
    def __init__(self, element_name: str, message: str) -> None:
        super().__init__(element_name, message)


class GameOver(SystemEvent):
    def __init__(self, message: str = "Game Over") -> None:
        super().__init__(message)

# class AIEvent(Protocol):

#     def to_action(self) -> Action:
#         ...


# class AIEventNone:
#     def __init__(self, entity: AICharactor) -> None:
#         self.entity = entity
#         self.target = None
#         self.location = None
    
#     def to_action(self) -> Action:
#         return NoAction(self.entity)

# class AIEventPathToTarget:
#     def __init__(self, entity: AICharactor, location: MapCoords) -> None:
#         self.entity = entity
#         self.target = None
#         self.location = location

#     def to_action(self) -> Action:
#         return MoveAction(self.entity, self.location)
    
# class AIEventTargetInMeleeRange:
#     def __init__(self, entity: AICharactor, target: Charactor) -> None:
#         self.entity = entity
#         self.target = target
#         self.location = None

#     def to_action(self) -> Action:
#         return MeleeAction(self.entity, self.target)
        