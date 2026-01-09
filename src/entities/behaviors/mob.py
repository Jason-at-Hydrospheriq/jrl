#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, cast

from delays import GLOBAL_ACTION_COOLDOWN_TIME
from game_types import TileCoordinate, StateActionObject
from baseclasses import BaseActionOnEntity, BaseEntityEvent, BaseGameEvent, action_locked
from entities.library import Character, AICharacter, CombatEntity

if TYPE_CHECKING:
    from store import GameStore
    from loop.components import SubLoopHandler

###
# A BEHAVIOR is the pair of an EVENT and an ACTION that together define a discrete unit of functionality for an entity.
# The EVENT encapsulates the occurrence that triggers an ACTION, while the ACTION defines the specific operations.
# An EVENT can only be linked to one ACTION, but an ACTION can be triggered by multiple EVENTS.
# This design allows for modular and reusable behavior definitions that can be easily managed within the game loop
# architecture.
###

###
# An EVENT should follow this pattern:
# CALLED BY: An entity or system when a specific condition occurs that requires handling.
# 1. Encapsulate all relevant information about the occurrence that needs to be passed to the associated ACTION in the behavior.
# 2. Implement a trigger method that, when called, sends the EVENT to the appropriate loop handler for processing.
###

####
# An ACTION should follow this pattern:
# CALLED BY: An EVENT that is created by an entity or system OR directly called by another ACTION to form a chained sequence of ACTIONS.
# 1. Check pre-conditions (e.g., is the entity able to perform the action? At least the action_locked check should be done here)
# 2. Perform the action's main logic.
#    - Typically involves running through the entity's state machine to determine outcomes based on current state and action parameters.
#    - Should NOT directly trigger state updates. These triggers should be handled by the enity's state machine as a result of the action's effects.
# 3. Handle post-action effects (e.g. trigger follow-up events, log outcomes).
#    - Chained ACTIONS have two options:
#       a) Directly call the next ACTION in the sequence. This creates a synchronous flow between actions.
#       b) Create and an EVENT or ACTION and send it to the loop handler. This allows for asynchronous and flexible action sequences.
####


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
        super().__init__(store=store, handler=handler, entity=entity)

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
        if self.entity and self.entity.action_locked:
            return
        
        if isinstance(self.entity, AICharacter) and self.store is not None:
            step_size = 0
            if self.entity.location and self.entity.destination: # Calculate step size for movement
                x_step = self.entity.location.x - self.entity.destination.x if self.entity.destination else 0
                y_step = self.entity.location.y - self.entity.destination.y if self.entity.destination else 0
                step_size = max(abs(x_step), abs(y_step))

            if step_size <= 0 or step_size > 1: # Recalculate the path if step_size is invalid
                self.entity.set_destination_from_path()
            
            EntityMoveAction(store=self.store, handler=self.handler, entity=self.entity, destination=self.entity.destination).perform()  # type: ignore

            match self.entity.focus.state:  # type: ignore | State machine attribute created dynamically
                case 'idle':
                    pass

                case 'searching':
                    pass

                case 'tracking':
                    if self.entity.distance_to_target is not None and self.entity.distance_to_target > 1: # If not adjacent to target, recalculate path, and continue pursuit
                        self.entity.set_destination_from_path() # If not adjacent to target, recalculate path, and continue pursuit
                        AIPursuitEvent(store=self.store, handler=self.handler, entity=self.entity).trigger()
                        self.store.log.add(text=f"The {self.entity.name} is pursuing {self.entity.target.name}.")  # type: ignore | Entity in this state must have a target.

                case 'targeting':
                    if self.entity.distance_to_target == 1: # # type: ignore | State machine attribute created dynamically | Dummy combat action for now
                        if isinstance(self.entity, CombatEntity) and self.entity.target:
                            if not isinstance(self.entity.target, self.entity.__class__):  # Prevent attacking self types
                                EntityAttackAction(store=self.store, handler=self.handler, entity=self.entity, target=self.entity.target).perform()  # type: ignore | The store for this action must be GameStore.

pursue = ('aipursuitevent', AIPursuitAction())


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

