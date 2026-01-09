#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from time import sleep
from typing import TYPE_CHECKING, Tuple, cast
import numpy as np
import tcod

from game_types import TileCoordinate
from baseclasses import BaseGameEvent, action_locked
from entities import Character
from baseclasses import BaseGameAction
from entities.behaviors.entity import EntityMoveAction
from game_types import StateActionObject, TileCoordinate

if TYPE_CHECKING:
    from store import GameStore
    from loop.components import SubLoopHandler

GLOBAL_ACTION_COOLDOWN_TIME = 100  # Global cooldown time in milliseconds


@action_locked
class PlayerCharacter(Character):
    action_locked: bool | None = True
    location: TileCoordinate | None

    def __init__(   self,
                store: GameStore | None = None,
                location: TileCoordinate | None = None,
                *,
                name: str = "<Unnamed>",
                symbol: str = '@',
                color: Tuple[int, int, int]=(255, 255, 255),
                hp: int = 100,
                max_hp: int = 100,
                speed: int = 20,
                ) -> None:

        self.fov_radius = 6 # Must be set before super().__init__() call to ensure FOV is correct on initialization.
        self.location = location # Must be set before super().__init__() call to ensure FOV is correct on initialization.

        super().__init__(store=store, symbol=symbol, color=color, name=name)
        self.hp = hp
        self.max_hp = max_hp
        self.speed = speed
        self.update()

    def update_fov(self) -> None:
        self.update_visible_tiles()
        if self.store: # type: ignore | Assume store is GameStore
            if self.visible_tiles is not None:
                self.store.atlas.active.set_state_bits('visible', self.visible_tiles)  # type: ignore | Assume store is GameStore

            # If a tile is "visible" it should be added to "explored".
            if self.store.atlas:  # type: ignore | Assume store is GameStore
                seen_tiles = self.store.atlas.active.seen  # type: ignore | Assume store is GameStore
                if isinstance(seen_tiles, np.ndarray) and self.visible_tiles is not None: # type: ignore | Assume store is GameStore
                    newly_seen_tiles = np.logical_or(seen_tiles, self.visible_tiles)
                    self.store.atlas.active.set_state_bits('seen', newly_seen_tiles)  # type: ignore | Assume store is GameStore

    def update(self) -> None:
        self.update_fov()
        super().update()

        
class InputEvent(BaseGameEvent):
    _input_event: tcod.event.Event | None

    def __init__(self, store: GameStore | None = None, handler: SubLoopHandler | None = None, input_event: tcod.event.Event | None = None) -> None:
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

    def __init__(self, store: GameStore | None = None, handler: SubLoopHandler | None = None, input_event: tcod.event.KeyboardEvent | None = None) -> None:
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
    
    def __init__(self, store: GameStore | None = None, handler: SubLoopHandler | None = None, entity: Character | None = None, target: Character | None = None) -> None:
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



