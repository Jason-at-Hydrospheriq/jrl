#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from core_components.events.base import BaseGameEvent


class SystemEvent(BaseGameEvent):

    def __init__(self, message: str) -> None:
        self.message = message


class GameStartEvent(SystemEvent):
    def __init__(self, message: str = "Game Start") -> None:
        super().__init__(message)


class GameOverEvent(SystemEvent):
    pass


# class EntityEvent(BaseGameEvent):
#     entity: BaseEntity
#     message: str

#     def __init__(self, entity: BaseEntity, message: str) -> None:
#         self.entity = entity
#         self.message = message


# class NoCollision(EntityEvent):
#     def __init__(self, entity: BaseEntity, message: str) -> None:
#         super().__init__(entity, message)


# class WallCollision(EntityEvent):
#     def __init__(self, entity: BaseEntity, message: str) -> None:
#         super().__init__(entity, message)


# class MapBoundaryCollision(EntityEvent):
#     def __init__(self, entity: BaseEntity, message: str) -> None:
#         super().__init__(entity, message)


# class TargetCollision(EntityEvent):
#     def __init__(self, entity: BaseEntity, message: str) -> None:
#         super().__init__(entity, message)
    

# class MeleeCollision(EntityEvent):
#     def __init__(self, entity: BaseEntity, message: str) -> None:
#         super().__init__(entity, message)


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
        