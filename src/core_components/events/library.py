#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import tcod.event

from core_components.events.base import BaseGameEvent
from core_components.entities.library import BaseEntity, Charactor

class SystemEvent(BaseGameEvent):

    def __init__(self, message: str) -> None:
        self.message = message


class GameStartEvent(SystemEvent):
    def __init__(self, message: str = "Game Start") -> None:
        super().__init__(message)


class GameOverEvent(SystemEvent):
    pass


class InputEvent(BaseGameEvent):
    event: tcod.event.Event

    def __init__(self, event: tcod.event.Event, message: str = "TCOD Event", ) -> None:
        self.message = message
        self.event = event


class EntityEvent(BaseGameEvent):
    entity: BaseEntity
    message: str

    def __init__(self, entity: BaseEntity, message: str) -> None:
        self.entity = entity
        self.message = message


class NoCollision(EntityEvent):
    def __init__(self, entity: BaseEntity, message: str) -> None:
        super().__init__(entity, message)


class WallCollision(EntityEvent):
    def __init__(self, entity: BaseEntity, message: str) -> None:
        super().__init__(entity, message)


class MapBoundaryCollision(EntityEvent):
    def __init__(self, entity: BaseEntity, message: str) -> None:
        super().__init__(entity, message)


class TargetCollision(EntityEvent):
    def __init__(self, entity: BaseEntity, message: str) -> None:
        super().__init__(entity, message)
    

class MeleeCollision(EntityEvent):
    def __init__(self, entity: BaseEntity, message: str) -> None:
        super().__init__(entity, message)

class CombatEvent(EntityEvent):
    def __init__(self, entity: BaseEntity, target: BaseEntity, message: str) -> None:
        super().__init__(entity, message)
        self.target: BaseEntity | None = target

class MeleeAttack(CombatEvent):
    def __init__(self, entity: Charactor, target: Charactor, message: str) -> None:
        super().__init__(entity, target, message)
        self.entity = entity
        self.target = target


class RangedAttack(CombatEvent):
    pass


class SpellCast(CombatEvent):
    pass


class FOVUpdateEvent(SystemEvent):
    def __init__(self, message: str) -> None:
        super().__init__(message)
    """Triggers the FOV update for all entities."""


class UIEvent(BaseGameEvent):
    element_name: str
    message: str

    def __init__(self, element_name: str, message: str) -> None:
        self.element_name = element_name
        self.message = message


class MapUpdateEvent(UIEvent):
    def __init__(self, element_name: str, message: str) -> None:
        super().__init__(element_name, message)


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
        