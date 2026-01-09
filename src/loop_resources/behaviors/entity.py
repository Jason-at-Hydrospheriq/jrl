#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import sys
from time import sleep
import traceback
from typing import TYPE_CHECKING, cast

from entities import BaseGameEntity, MobileEntity, TargetableEntity, TargetingEntity, CombatEntity
from loop_resources.behaviors.base import BaseActionOnDestination, BaseGameEvent, BaseActionOnEntity, BaseActionOnTarget, GLOBAL_ACTION_COOLDOWN_TIME
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
        raise NotImplementedError("Subclasses must implement trigger method")


class EntityTargetEvent(EntityEvent):
    _target: BaseGameEntity | None

    def __init__(self, store: GameStore | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None, target: BaseGameEntity | None = None) -> None:
        super().__init__(store, handler, entity)
        self.target = target

    @property
    def target(self) -> BaseGameEntity | None:
        return self._target
    
    @target.setter
    def target(self, value: BaseGameEntity | None) -> None:
        if value is not None and not isinstance(value, BaseGameEntity):
            raise TypeError("target must be an instance of BaseGameEntity or None")
        self._target = value

    def trigger(self) -> None:
        raise NotImplementedError("Subclasses must implement trigger method")


class EntityMoveAction(BaseActionOnDestination):

    def __init__(self, store: GameStore | None = None, handler:  StateHandler | None = None, entity: MobileEntity | None = None, 
                 destination: TileCoordinate | None = None) -> None:
        super().__init__(store, handler, entity, destination)

    def perform(self) -> None:
        if self.entity and self.entity.action_locked:
            return
        
        if isinstance(self.entity, MobileEntity) and self.store and self.destination:
            self.entity.destination = self.destination
            self.entity.update()
            
            initial_state = self.entity.collision.state  # type: ignore | State machine attribute created dynamically
            recalculate = False

            wait = GLOBAL_ACTION_COOLDOWN_TIME // 2 # Default wait time
            if self.entity.speed:
                wait = (GLOBAL_ACTION_COOLDOWN_TIME - self.entity.speed) // 2
            
            EntityWaitAction(wait_time=wait, store=self.store, handler=self.handler, entity=self.entity).perform() # type: ignore | The store for this action must be GameStore.

            match self.entity.collision.state:  # type: ignore | State machine attribute created dynamically
                case 'not_colliding':                     
                    self.entity.move()
                
                case 'colliding_with_terrain':
                    if hasattr(self.entity, 'path'):  # type: ignore | State machine attribute created dynamically
                        self.entity.path = []  # type: ignore | State machine attribute created dynamically
                        self.entity.destination = None  #type: ignore | State machine attribute created dynamically
                        recalculate = True

                case 'colliding_with_boundary':
                    if hasattr(self.entity, 'path'):  # type: ignore | State machine attribute created dynamically
                        recalculate = True
                        self.entity.path = []  # type: ignore | State machine attribute created dynamically
                        self.entity.destination = None  #type: ignore | State machine attribute created dynamically

                case 'colliding_with_entity':
                    if isinstance(self.entity, TargetingEntity):
                        target = self.store.portfolio.get_entity_at_location(self.entity.destination)[0]  # type: ignore | The store for this action must be GameStore.
                        if not isinstance(target, self.entity.__class__):  # Prevent targeting self types
                            self.entity.set_target(target)  

                    if isinstance(self.entity, CombatEntity) and self.entity.target:
                        if not isinstance(self.entity.target, self.entity.__class__):  # Prevent attacking self types
                            EntityAttackAction(store=self.store, handler=self.handler, entity=self.entity, target=self.entity.target).perform()  # type: ignore | The store for this action must be GameStore.

            if recalculate and not initial_state == self.entity.collision.state:  # type: ignore | State machine attribute created dynamically, break loop if state hasn't changed
                self.recalculate_move()

    def recalculate_move(self) -> None:
        if hasattr(self.entity, 'set_destination_from_path'):
            self.entity.set_destination_from_path() # type: ignore | Need to get types and inheritance straightened out here.
            EntityMoveAction(store=self.store, handler=self.handler, entity=self.entity, destination=self.entity.destination).perform()  # type: ignore | The store for this action must be GameStore.

        
class EntityWaitEvent(EntityEvent):
    wait_time: int

    def __init__(self, store: GameStore | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None, wait_time: int = 0) -> None:
        super().__init__(store, handler, entity)
        self.wait_time = wait_time

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))      


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

entitywait = ('entitywaitevent', EntityWaitAction())


class EntityAttackEvent(EntityTargetEvent):

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class EntityAttackAction(BaseActionOnTarget):

    def __init__(self, store: GameStore | None = None, handler:  StateHandler | None = None, entity: CombatEntity | None = None, 
                 target: BaseGameEntity | None = None) -> None:
        super().__init__(store, handler, entity, target)

    def perform(self) -> None:

        if self.entity and self.entity.action_locked or not isinstance(self.entity, TargetableEntity):
            return
        
        try:
            if isinstance(self.entity, CombatEntity) and self.store and self.target:
                wait = GLOBAL_ACTION_COOLDOWN_TIME // 2 # Default wait time
                if hasattr(self.entity, 'speed') and self.entity:
                    wait = (GLOBAL_ACTION_COOLDOWN_TIME- self.entity.speed) // 2  # type: ignore
                
                EntityWaitAction(wait_time=wait, store=self.store, handler=self.handler, entity=self.entity).perform() # type: ignore | The store for this action must be GameStore.
                
                match self.entity.combat.state:  # type: ignore | State machine attribute created dynamically'
                    case 'peaceful':
                        pass

                    case 'disengaged':
                        pass

                    case 'engaged':
                        pass

                    case 'fighting': 
                        
                        if not self.target.health.is_dead():  # type: ignore | Gotta get types and inheritance straightened out here.         
                            damage = self.entity.attack()  
                            defend = 0
                            if isinstance(self.target, CombatEntity):
                                defend = self.target.defend()

                            damage = max(0, damage - defend)
                            
                            if damage > 0:
                                self.target.take_damage(damage) # type: ignore | Gotta get types and inheritance straightened out here.
                                if 'remains' not in self.target.name.lower():
                                     self.store.log.add(f"{self.entity.name} attacks {self.target.name} for {damage} damage!")  # type: ignore | The store for this action must be GameStore.
                                else:
                                    self.store.log.add(f"Easy {self.entity.name}. Way to kick a guy while they're down!")  # type: ignore | The store for this action must be GameStore.
            
        except Exception as e:
            print(f"Error performing attack action: {e}.")
            traceback.print_exc(file=sys.stdout)

entityattack = ('entityattackevent', EntityAttackAction())