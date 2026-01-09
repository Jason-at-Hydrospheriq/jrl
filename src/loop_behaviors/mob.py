#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, List, cast, Tuple
from unittest import case
import numpy as np
from tcod.path import SimpleGraph, Pathfinder

from entity_components.library import Character
from loop_behaviors.base import BaseGameEvent, BaseActionOnEntity, BaseEntityEvent
from loop_behaviors.entity import EntityWaitEvent, EntityMoveAction
from game_types import StateActionObject
from atlas_components.tiles import TileCoordinate
from entity_components.base import action_locked

if TYPE_CHECKING:
    from engine_components import GameStore
    from engine_components.loop import SubLoopHandler

GLOBAL_ACTION_COOLDOWN_TIME = 100  # Global cooldown time in milliseconds


# ENTITIES
@action_locked
class AICharacter(Character):
    path: List[TileCoordinate] = []
    _ai: SubLoopHandler | None = None
    
    def __init__(   self,
                    store: GameStore | None = None,
                        *,
                    location: TileCoordinate | None = None,
                    name: str = "<Unnamed>",
                    symbol: str = '?',
                    color: Tuple[int, int, int]=(255, 255, 255),
                    ai: SubLoopHandler | None = None,
                    ) -> None:
        
        if ai:
            self._ai = ai
            
        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)

    @property
    def ai(self) -> SubLoopHandler | None:
        return self._ai

    @ai.setter
    def ai(self, value: SubLoopHandler | None) -> None:
        self._ai = value

    def set_path_to_target(self) -> None:
        if self.target and self.location and self.store and self.store.atlas and self.target.location is not None:  # type: ignore | Assume store is GameStore
            map_size = self.store.atlas.active.grid.size  # type: ignore | Assume store is GameStore
            blocked_tiles = np.array(self.store.atlas.active.blocks_movement, dtype=np.int8) # type: ignore | Assume store is GameStore
            blocked_tiles += 10
            cost = SimpleGraph(cost=blocked_tiles, cardinal=2, diagonal=5)
            finder = Pathfinder(cost)  # type: ignore | Assume store is GameStore
            finder.add_root(self.location.to_tuple)
            path = finder.path_to(self.target.location.to_tuple)
            self.path = [TileCoordinate.from_tuple((step[0], step[1]), parent_map_size=map_size) for step in path]
        else:
            self.path = []
        self.update()

    def set_destination_from_path(self) -> None:
        if self.path:
            self.path.pop(0)  # Remove current location from path
            self.destination = self.path.pop(0) if self.path else None
        else:
            self.set_path_to_target()
            self.set_destination_from_path()

        self.update()

    def die(self) -> None:
        super().die()
        self._ai = None

    def update(self) -> None:
        super().update()


@action_locked
class MobCharacter(AICharacter):
    action_locked: bool | None = False
    location: TileCoordinate | None

    def __init__(   self,
                    store: GameStore | None = None,
                    *,
                    location: TileCoordinate | None = None,
                    name: str = "<Unnamed>",
                    symbol: str = '?',
                    color: Tuple[int, int, int]=(255, 255, 255),
                    hp: int = 50,
                    max_hp: int = 50,
                    ) -> None:

        self.fov_radius = 5 # Must be set before super().__init__() call to ensure FOV is correct on initialization.
        self.location = location # Must be set before super().__init__() call to ensure FOV is correct on initialization.

        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)
        
        self.hp = hp
        self.max_hp = max_hp
        self.update()

    @property
    def ai(self) -> SubLoopHandler | None:
        return self._ai
    
    @ai.setter
    def ai(self, value: SubLoopHandler | None) -> None:   # type: ignore
        self._ai = value

    def update(self) -> None:
        super().update()
        if self.ai:
            if self.ai.events.qsize() < 10 and self.ai.actions.qsize() < 10:
                if self.store and self.store.portfolio:  # type: ignore | Assume store is GameStore
                    self.ai.handle(AIUpdateFocusEvent(store=self.store, handler=self.ai, entity=self))


# BEHAVIORS
class AICharacterEvent(BaseGameEvent):
    _entity: AICharacter | None
    _target: Character | None

    def __init__(self, store: GameStore | None = None, handler: SubLoopHandler | None = None, entity: AICharacter | None = None, target: Character | None = None) -> None:
        super().__init__(store, handler)
        self._entity = entity
        self._target = target
    
    @property
    def entity(self) -> AICharacter | None:
        return self._entity
    
    @entity.setter
    def entity(self, value: AICharacter | None) -> None:
        if value is not None and not isinstance(value, AICharacter):
            raise TypeError("entity must be an instance of AICharacter or None")
        self._entity = value

    @property
    def target(self) -> Character | None:
        return self._target
    
    @target.setter
    def target(self, value: Character | None) -> None:
        if value is not None and not isinstance(value, Character):
            raise TypeError("target must be an instance of Character or None")
        self._target = value

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class AIUpdateFocusEvent(BaseEntityEvent):
    """
    The AIUpdateFocusEvent is the event portion of the UpdateFocus behavior for a TargetingEntity controlled by the GameAI. It is created by the Game AI or directly by an AICharacter.
    Duck Types: StateActionObject, StoredStateObject
    """
    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class AIUpdateFocusAction(BaseActionOnEntity):
    """
    The AIUpdateFocusAction is the action portion of the UpdateFocus behavior for a TargetingEntity controlled by the GameAI. It is performed by an AICharacter.
    
    Duck Types: StateActionObject, StoredStateObject
    """
    def __init__(self, store: GameStore | None = None, handler:  SubLoopHandler | None = None, entity: AICharacter | None = None) -> None:
        super().__init__(store, handler, entity)

    def perform(self) -> None:

        if isinstance(self.entity, AICharacter) and self.store is not None:
            if not self.entity.action_locked and self.handler:

                match self.entity.focus.state:  # type: ignore | State machine attribute created dynamically
                    case 'idle':
                        if self.entity.is_location_in_earshot(self.store.portfolio.player.location):  # type: ignore | Assume store is GameStore
                            self.handler.handle(AIAcquireTargetEvent(store=self.store, handler=self.handler, entity=self.entity))

                    case 'searching':
                        pass 

                    case 'tracking':
                        if self.entity.focus.state_changed:  # type: ignore | State machine attribute created dynamically
                            self.handler.handle(AIInvestigateEvent(store=self.store, handler=self.handler, entity=self.entity))
                            self.entity.state_changed = False  # type: ignore | State machine attribute created dynamically
                        elif self.entity.distance_to_target is not None and self.entity.distance_to_target > 1:
                            self.entity.set_destination_from_path()
                            self.handler.handle(AIPursuitEvent(store=self.store, handler=self.handler, entity=self.entity)) # type: ignore

                    case 'targeting':
                        if self.entity.distance_to_target is not None and self.entity.distance_to_target > 1:
                            self.entity.set_destination_from_path()
                            self.handler.handle(AIPursuitEvent(store=self.store, handler=self.handler, entity=self.entity)) # type: ignore
                        elif self.entity.distance_to_target == 1:
                            self.handler.handle(None)  # type: ignore | Dummy combat event for now
                            self.store.log.add(f"The {self.entity.name} kicks {self.entity.target.name}!")  # type: ignore | Entity in this state must have a target.
                    case _:
                        pass

update_focus = ('aiupdatefocusevent', AIUpdateFocusAction())


class AIAcquireTargetEvent(BaseEntityEvent):
    """
    The AIAcquireTargetEvent is the event portion of the AcquireTarget behavior for a TargetingEntity controlled by the GameAI. It is created by the Game AI or directly by an AICharacter.
    Duck Types: StateActionObject, StoredStateObject
    """
    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class AIAcquireTargetAction(BaseActionOnEntity):
    """
    The AIAcquireTargetAction is the action portion of the AcquireTarget behavior for a TargetingEntity controlled by the GameAI. It is performed by an AICharacter.
    
    Duck Types: StateActionObject, StoredStateObject
    """
    def __init__(self, store: GameStore | None = None, handler:  SubLoopHandler | None = None, entity: AICharacter | None = None) -> None:
        super().__init__(store, handler, entity)

    def perform(self) -> None:

        if isinstance(self.entity, AICharacter) and self.store is not None:
            if not self.entity.action_locked:
                self.entity.acquire_target()
                self.entity.update()

                if self.entity.target is not None:
                    match self.entity.focus.state:  # type: ignore | State machine attribute created dynamically
                        case 'searching':
                            text = f"The {self.entity.name}'s guard is up."
                        case 'tracking':
                            text = f"The {self.entity.name} has spotted {self.entity.target.name}"  # type: ignore | Entity in this state must have a target.
                        case 'targeting':
                            text = f"The {self.entity.name} is looking at {self.entity.target.name} with malice."  # type: ignore | Entity in this state must have a target.
                        case 'idle':
                            text = f"The {self.entity.name} looks bored."
                        case _:
                            text = f"The {self.entity.name} looks confused."

                    self.store.log.add(text=text)  # type: ignore | AICharacter must have a GameStore to log messages.
            
                    if self.handler:
                        self.handler.send(EntityWaitEvent(wait_time=GLOBAL_ACTION_COOLDOWN_TIME, store=self.store, handler=self.handler, entity=self.entity))  # type: ignore

acquire_target = ('aiacquiretargetevent', AIAcquireTargetAction())


class AIInvestigateEvent(BaseEntityEvent):
    """
    The AIInvestigateEvent is the event portion of the Investigate behavior for a TargetingEntity controlled by the GameAI. It is created by the Game AI or directly by an AICharacter.
    Duck Types: StateActionObject, StoredStateObject
    """
    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class AIInvestigateAction(BaseActionOnEntity):
    """
    The AIInvestigateAction is the action portion of the Investigate behavior for a TargetingEntity controlled by the GameAI. It is performed by an AICharacter.
    
    Duck Types: StateActionObject, StoredStateObject
    """
    def __init__(self, store: GameStore | None = None, handler:  SubLoopHandler | None = None, entity: AICharacter | None = None) -> None:
        super().__init__(store, handler, entity)

    def perform(self) -> None:

        if isinstance(self.entity, AICharacter) and self.store is not None:
            if not self.entity.action_locked:
                if self.entity.focus.is_tracking():  # type: ignore | State machine attribute created dynamically
                    if self.entity.distance_to_target is not None and self.entity.distance_to_target > 1: # Do nothing if adjacent
                        self.entity.set_destination_from_path()

                        self.store.log.add(text=f"The {self.entity.name} is moving to investigate {self.entity.target.name}.")  # type: ignore | Entity in this state must have a target. | If collision detected, recalculate path

                        AIPursuitAction(store=self.store, handler=self.handler, entity=self.entity).perform()  # type: ignore

investigate = ('aiinvestigateevent', AIInvestigateAction())


class AIPursuitEvent(BaseEntityEvent):
    """
    The AIPursuitEvent is the event portion of the Pursuit behavior for a TargetingEntity controlled by the GameAI. It is created by the Game AI or directly by an AICharacter.
    Duck Types: StateActionObject, StoredStateObject
    """
    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class AIPursuitAction(BaseActionOnEntity):
    """
    The AIPursuitAction is the action portion of the Pursuit behavior for a TargetingEntity controlled by the GameAI. It is performed by an AICharacter.
    
    Duck Types: StateActionObject, StoredStateObject
    """
    def __init__(self, store: GameStore | None = None, handler:  SubLoopHandler | None = None, entity: AICharacter | None = None) -> None:
        super().__init__(store, handler, entity)

    def perform(self) -> None:

        if isinstance(self.entity, AICharacter) and self.store is not None:
            step_size = 0
            if self.entity.location and self.entity.destination: # Calculate step size for movement
                x_step = self.entity.location.x - self.entity.destination.x if self.entity.destination else 0
                y_step = self.entity.location.y - self.entity.destination.y if self.entity.destination else 0
                step_size = max(abs(x_step), abs(y_step))

            if step_size <= 0 or step_size > 1: # Recalculate the path if step_size is invalid
                self.entity.set_destination_from_path()
            
            if not self.entity.action_locked:
               if self.entity.collision.state == 'not_colliding':  # type: ignore | State machine attribute created dynamically
                   EntityMoveAction(store=self.store, handler=self.handler, entity=self.entity, destination=self.entity.destination).perform()  # type: ignore
            
            if self.handler:
                if self.entity.focus.state == 'tracking' or self.entity.focus.state == 'targeting':  # type: ignore | State machine attribute created dynamically
                    if self.entity.distance_to_target > 1:
                        self.entity.set_destination_from_path() # If not adjacent to target, recalculate path, and continue pursuit
                        self.handler.handle(AIPursuitEvent(store=self.store, handler=self.handler, entity=self.entity))
                        self.store.log.add(text=f"The {self.entity.name} is pursuing {self.entity.target.name}.")  # type: ignore | Entity in this state must have a target.

                if self.entity.focus.state == 'targeting' and self.entity.distance_to_target == 1: # # type: ignore | State machine attribute created dynamically | Dummy combat action for now
                    self.store.log.add(f"The {self.entity.name} kicks {self.entity.target.name}!")  # type: ignore | Entity in this state must have a target.

pursue = ('aipursuitevent', AIPursuitAction())