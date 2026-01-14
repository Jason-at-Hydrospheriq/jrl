#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import sys
from time import sleep
import traceback
from typing import TYPE_CHECKING, cast

from baseclasses import BaseActionOnDestination, BaseActionOnEntity, BaseActionOnTarget, BaseGameAction, BaseGameEntity, BaseGameEvent, BaseItem
from entities.actors import MobileEntity, TargetableEntity, TargetingEntity, CombatEntity, Character
from delays import GLOBAL_ACTION_COOLDOWN_TIME
from game_types import StateActionObject, StateHandler, TileCoordinate

if TYPE_CHECKING:
    from store import GameStore
    from loop.components import SubLoopHandler


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

            wait = GLOBAL_ACTION_COOLDOWN_TIME # Default wait time
            if self.entity.speed:
                wait = (GLOBAL_ACTION_COOLDOWN_TIME - (50 - self.entity.speed))  # type: ignore
            
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
                        target = self.store.portfolio.get_entity_at_location(self.entity.destination)  # type: ignore | The store for this action must be GameStore.
                        if len(target) > 0:
                            target = target[0]
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
            wait_time = max(0, self.wait_time)
            self.entity.action_locked = True  # Lock the entity's actions during the wait
            sleep(wait_time / 1000.0) # Convert milliseconds to seconds
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
            if self.entity and self.entity.action_locked:
                return
            
            if isinstance(self.entity, CombatEntity) and self.store and self.target:
                wait = GLOBAL_ACTION_COOLDOWN_TIME # Default wait time
                if hasattr(self.entity, 'speed') and self.entity:
                    wait = GLOBAL_ACTION_COOLDOWN_TIME + (50 - self.entity.speed)  # type: ignore
                
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
                            attack = attack = self.entity.attack()
                            defend = 0
                            damage = 0

                            match self.entity.health.state:  # type: ignore | State machine attribute created dynamically
                                # case 'healthy' | 'injured':
                                #     pass
                                case 'critical':
                                    attack = max(1, attack * 3 // 4)
                                
                            if isinstance(self.target, CombatEntity):
                                defend = self.target.defend()

                                match self.target.health.state:  # type: ignore | State machine attribute created dynamically
                                    # case 'healthy' | 'injured':
                                    #     pass
                                    case 'critical':
                                        defend = max(1, defend * 3 // 4)

                            if attack and defend:
                                damage = max(0, attack - defend)
                            
                            elif attack:
                                damage = attack

                            if damage > 0:
                                self.target.take_damage(damage) # type: ignore | Gotta get types and inheritance straightened out here.

        except Exception as e:
            print(f"Error performing attack action: {e}.")
            traceback.print_exc(file=sys.stdout)

entityattack = ('entityattackevent', EntityAttackAction())


class EntityUseItemAction(BaseGameAction):
    item_name: str

    def __init__(self, store: GameStore | None = None, handler: SubLoopHandler | None = None, item_name: str = "") -> None:
        super().__init__(store, handler)
        self.item_name = item_name

    def perform(self) -> None:
        if self.store and self.store.portfolio.player:  # type: ignore | The store for this action must be GameStore.
            item = self.store.portfolio.player.inventory.get(self.item_name)  # type: ignore | The store for this action must be GameStore.
            if item:
                item.use()  # type: ignore | The store for this action must be GameStore.


class EntityPickupAction(BaseActionOnDestination):
    def perform(self) -> None:
        if self.store and self.store.portfolio and self.entity and self.destination: # type: ignore | Assume store is GameStore
            items_at_location = self.store.portfolio.get_entity_at_location(self.destination)  # type: ignore | Assume store is GameStore
            if items_at_location:
                for item in items_at_location:
                    if isinstance(self.entity, Character):
                        # Make this a state check for inventory full/slot full later
                        if self.entity and self.entity.inventory:
                            if isinstance(item, BaseItem) and not item.owner:  
                                self.entity.inventory.add(item)  