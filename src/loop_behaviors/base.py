#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from entity_components.base import BaseGameEntity
from game_types import StateHandler
from atlas_components.tiles.base import TileCoordinate
from game_types import *


GLOBAL_ACTION_COOLDOWN_TIME = 100  # Global cooldown time in milliseconds


class BaseGameEvent:
    store: StatefulObject | None
    handler: StateHandler | None
    
    def __init__(self, store: StatefulObject | None = None, handler: StateHandler | None = None) -> None:
        self.store = store
        self.handler = handler
        
    def trigger(self) -> None:
        raise NotImplementedError("Subclasses must implement the trigger method.")
        

class BaseEntityEvent(BaseGameEvent):
    entity: BaseGameEntity | None

    def __init__(self, store: StatefulObject | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None) -> None:
        super().__init__(store, handler)

        self.entity = entity

    def trigger(self) -> None:
        raise NotImplementedError("Subclasses must implement the trigger method.")
    
    
class BaseGameAction:
    store: StatefulObject | None
    handler: StateHandler | None
    
    def __init__(self, store: StatefulObject | None = None, handler: StateHandler | None = None) -> None:
        self.store = store
        self.handler = handler

    def perform(self) -> None:
        raise NotImplementedError("Subclasses must implement the perform method.")
    

class BaseActionOnEntity(BaseGameAction):
    entity: BaseGameEntity | None

    def __init__(self, store: StatefulObject | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None) -> None:
        super().__init__(store, handler)

        self.entity = entity

    def perform(self) -> None:
        raise NotImplementedError("Subclasses must implement the perform method.")
    

class BaseActionOnTarget(BaseGameAction):
    entity: BaseGameEntity | None = None
    target: BaseGameEntity | None = None

    def __init__(self, store: StatefulObject | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None, 
                 target: BaseGameEntity | None = None) -> None:
        super().__init__(store, handler)

        self.entity = entity
        self.target = target

    def perform(self) -> None:
        raise NotImplementedError("Subclasses must implement the perform method.")


class BaseActionOnDestination(BaseGameAction):
    entity: BaseGameEntity | None = None
    destination: TileCoordinate | None = None

    def __init__(self, store: StatefulObject | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None, 
                 destination: TileCoordinate | None = None) -> None:
        super().__init__(store, handler)

        self.entity = entity
        self.destination = destination

    def perform(self) -> None:
        raise NotImplementedError("Subclasses must implement the perform method.")
