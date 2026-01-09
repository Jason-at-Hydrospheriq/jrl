#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from entities import BaseGameEntity
from game_types import *

GLOBAL_ACTION_COOLDOWN_TIME = 100  # Global cooldown time in milliseconds


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
