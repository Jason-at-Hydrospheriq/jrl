#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from time import sleep
from typing import TYPE_CHECKING, cast

from entities.library import BaseGameEntity, MobileEntity, TargetingEntity
from loop_components.base import BaseActionOnDestination, BaseGameEvent, BaseActionOnEntity, GLOBAL_ACTION_COOLDOWN_TIME
from game_types import StateActionObject, StateHandler
from atlas_components.tiles.base import TileCoordinate

if TYPE_CHECKING:
    from engine_components import GameStore


class EntityEvent(BaseGameEvent):
    _entity: BaseGameEntity | None

    def __init__(self, store: GameStore | None = None, handler: StateHandler | None = None, entity: BaseGameEntity | None = None) -> None:
        super().__init__(store, handler)
        self._entity = entity

    @property
    def entity(self) -> BaseGameEntity | None:
        return self._entity
    
    @entity.setter
    def entity(self, value: BaseGameEntity | None) -> None:
        if value is not None and not isinstance(value, BaseGameEntity):
            raise TypeError("entity must be an instance of BaseGameEntity or None")
        self._entity = value

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class EntityWaitEvent(EntityEvent):
    wait_time: int

    def __init__(self, store: GameStore | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None, wait_time: int = 0) -> None:
        super().__init__(store, handler, entity)
        self.wait_time = wait_time


class EntityWaitAction(BaseActionOnEntity):
    """
    The EntityWaitAction is the action of the Wait behavior. It is called by an EntityWaitEvent created by an entity.
    
    Duck Types: StateActionObject, StoredStateObject
    """
    wait_time: int = 0  # Time to wait in milliseconds
    
    def __init__(self, store: GameStore | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None, wait_time: int = 0) -> None:
        super().__init__(store, handler, entity)
        self.wait_time = wait_time

    def perform(self) -> None:
        if self.entity:
            self.entity.action_locked = True  # Lock the entity's actions during the wait
            sleep(self.wait_time / 1000.0) # Convert milliseconds to seconds
            self.entity.action_locked = False  # Unlock the entity's actions after the wait

        if self.handler:
            self.handler.handle(None) # type: ignore


class EntityMoveAction(BaseActionOnDestination):

    def __init__(self, store: GameStore | None = None, handler:  StateHandler | None = None, entity: MobileEntity | None = None, 
                 destination: TileCoordinate | None = None) -> None:
        super().__init__(store, handler, entity, destination)

    def perform(self) -> None:
        if isinstance(self.entity, MobileEntity) and self.store and self.destination:
            self.entity.destination = self.destination
            self.entity.update()
            wait = 0
            if self.entity.speed:
                wait = (GLOBAL_ACTION_COOLDOWN_TIME - self.entity.speed) // 2

            match self.entity.collision.state:  # type: ignore | State machine attribute created dynamically
                case 'not_colliding':

                    if self.entity.action_locked is False:
                        EntityWaitAction(wait_time=wait, store=self.store, handler=self.handler, entity=self.entity).perform() # type: ignore | The store for this action must be GameStore.
                        self.entity.move()
                        self.entity.update()
                
                case 'colliding_with_terrain':
                    return  # Do nothing on terrain collision for now.
                
                case 'colliding_with_boundary':
                    return  # Do nothing on map boundary collision for now.
                
                case 'colliding_with_entity':
                    if isinstance(self.entity, TargetingEntity):
                        target = self.store.portfolio.get_entity_at_location(self.entity.destination)[0]  # type: ignore | The store for this action must be GameStore.
                        self.entity.set_target(target)  
                        self.entity.update()

                        if self.entity.action_locked is False:
                            EntityWaitAction(wait_time=wait, store=self.store, handler=self.handler, entity=self.entity).perform() # type: ignore | The store for this action must be GameStore.

