#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from time import sleep
from typing import TYPE_CHECKING, cast
import tcod

from entities.library import Character
from loop_components.base import BaseGameAction, BaseGameEvent
from loop_components.entity import EntityMoveAction
from game_types import StateActionObject
from atlas_components.tiles.base import TileCoordinate

if TYPE_CHECKING:
    from engine_components import GameStore
    from engine_components.ai import LoopHandler

GLOBAL_ACTION_COOLDOWN_TIME = 100  # Global cooldown time in milliseconds


class InputEvent(BaseGameEvent):
    _input_event: tcod.event.Event | None

    def __init__(self, store: GameStore | None = None, handler: LoopHandler | None = None, input_event: tcod.event.Event | None = None) -> None:
        super().__init__(store, handler)
        self._input_event = input_event

    @property
    def input_event(self) -> tcod.event.Event | None:
        return self._input_event

    @input_event.setter
    def input_event(self, value: tcod.event.Event | None) -> None:
        if value is not None and not isinstance(value, tcod.event.Event):
            raise TypeError("input_event must be an instance of tcod.event.Event or None")
        self._input_event = value

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class KeyDownAction(BaseGameAction):
    input_event: tcod.event.Event | None

    def __init__(self, store: GameStore | None = None, handler: LoopHandler | None = None, input_event: tcod.event.KeyboardEvent | None = None) -> None:
        super().__init__(store, handler)
        self.input_event = input_event

    def perform(self) -> None:
        if isinstance(self.input_event, tcod.event.KeyboardEvent):
            key_sim = self.input_event.sym if self.input_event else None
            destination = (0, 0)

            if self.store and self.store.portfolio.player and key_sim is not None:  # type: ignore | The store for this action must be GameStore.
                if self.store.portfolio.player.location:  # type: ignore | The store for this action must be GameStore.
                    destination = (self.store.portfolio.player.location.x, self.store.portfolio.player.location.y) # type: ignore | The store for this action must be GameStore.

                # Parse movement keys
                match key_sim:
                    case tcod.event.KeySym.LEFT:
                        destination = (destination[0] - 1, destination[1])
                    case tcod.event.KeySym.A:
                        destination = (destination[0] - 1, destination[1])
                    case tcod.event.KeySym.RIGHT:
                        destination = (destination[0] + 1, destination[1])
                    case tcod.event.KeySym.D:
                        destination = (destination[0] + 1, destination[1])
                    case tcod.event.KeySym.UP:
                        destination = (destination[0], destination[1] - 1)
                    case tcod.event.KeySym.W:
                        destination = (destination[0], destination[1] - 1)
                    case tcod.event.KeySym.DOWN:
                        destination = (destination[0], destination[1] + 1)
                    case tcod.event.KeySym.S:
                        destination = (destination[0], destination[1] + 1)
                
                if destination != (0,0):      
                    self.handler.send(EntityMoveAction(store=self.store, handler=self.handler, entity=self.store.portfolio.player,  # type: ignore | The store for this action must be GameStore.
                                                           destination=TileCoordinate.from_tuple(destination, parent_map_size=self.store.atlas.active.grid.size)))  # type: ignore | The store for this action must be GameStore.



class PlayerCharacterEvent(BaseGameEvent):
    _entity: Character | None
    _target: Character | None
    
    def __init__(self, store: GameStore | None = None, handler: LoopHandler | None = None, entity: Character | None = None, target: Character | None = None) -> None:
        super().__init__(store, handler)
        self._entity = entity
        self._target = target

    @property
    def entity(self) -> Character | None:
        return self._entity
    
    @entity.setter
    def entity(self, value: Character | None) -> None:
        if value is not None and not isinstance(value, Character):
            raise TypeError("entity must be an instance of Character or None")
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

