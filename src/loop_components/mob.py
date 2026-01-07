#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, cast

from entities.library import Character, AICharacter
from loop_components.base import BaseGameEvent, BaseActionOnEntity
from loop_components.entity import EntityWaitEvent

from game_types import StateActionObject

if TYPE_CHECKING:
    from engine_components import GameStore
    from engine_components.ai import LoopHandler

GLOBAL_ACTION_COOLDOWN_TIME = 100  # Global cooldown time in milliseconds


class AICharacterEvent(BaseGameEvent):
    _entity: AICharacter | None
    _target: Character | None

    def __init__(self, store: GameStore | None = None, handler: LoopHandler | None = None, entity: AICharacter | None = None, target: Character | None = None) -> None:
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


class AIAcquireTargetEvent(AICharacterEvent):
    """
    The AIAcquireTargetEvent is the event portion of the AcquireTarget behavior for a TargetingEntity controlled by the GameAI. It is created by the Game AI or directly by an AICharacter.
    Duck Types: StateActionObject, StoredStateObject
    """
    pass


class AIAcquireTargetAction(BaseActionOnEntity):
    """
    The AIAcquireTargetAction is the action portion of the AcquireTarget behavior for a TargetingEntity controlled by the GameAI. It is performed by an AICharacter.
    
    Duck Types: StateActionObject, StoredStateObject
    """
    def __init__(self, store: GameStore | None = None, handler:  LoopHandler | None = None, entity: AICharacter | None = None) -> None:
        super().__init__(store, handler, entity)

    def perform(self) -> None:

        if isinstance(self.entity, AICharacter) and self.store is not None:
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
                    self.handler.send(EntityWaitEvent(wait_time=100, store=self.store, handler=self.handler, entity=self.entity))  # type: ignore

