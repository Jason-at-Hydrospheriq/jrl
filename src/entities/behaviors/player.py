#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations  
from typing import TYPE_CHECKING, Tuple, cast
import numpy as np
import tcod

from entities.behaviors.system import NoAction, WaitAction, InputEvent
from entities.behaviors.entity import EntityMoveAction, EntityPickupAction, entitywait, entityattack
from entities.components import PlayerInventory
from game_types import TileCoordinate
from baseclasses import BaseGameEvent, BaseGameAction, action_locked
from entities.actors import AICharacter
from game_types import StateActionObject, TileCoordinate
import colors

if TYPE_CHECKING:
    from store import GameStore
    from loop.components import SubLoopHandler


@action_locked
class PlayerCharacter(AICharacter):
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
                speed: int = 30,
                ) -> None:

        self.fov_radius = 6 # Must be set before super().__init__() call to ensure FOV is correct on initialization.
        self.location = location # Must be set before super().__init__() call to ensure FOV is correct on initialization.

        super().__init__(store=store, symbol=symbol, color=color, name=name)
        self.hp = hp
        self.max_hp = max_hp
        self.speed = speed
        self.inventory = PlayerInventory(store=self)
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

    def take_damage(self, damage: int) -> None:
        super().take_damage(damage)

        # Update the log with the attack message
        message = ""
        if self.target and 'remains' not in self.target.name.lower():
            message = f"{self.target.name} attacks {self.name} for {damage} damage!"
        elif self.target and 'remains' in self.name.lower():
            message = f"Easy {self.target.name}. Way to kick a guy while they're down!"
        self.store.log.add(message, fg=colors.enemy_atk)  # type: ignore | The store for player must be GameStore.
    
    def take_turn(self, input_event: tcod.event.Event) -> None:
        if self.is_alive:  # type: ignore | Assume store is GameStore
            game_event = InputEvent(store=self.store, handler=self.ai, input_event=input_event)
            if self.ai:
                self.ai.handle(game_event)
        
        # All Visible Mobs Take Actions
        for mob in self.store.portfolio.visible_mobs:
            mob.take_turn() 

    def die(self) -> None:
        super().die()

        # Update the log and display state.
        self.color = colors.player_die  # type: ignore
        self.name = f"remains of {self.name}"
        self.store.log.add(f"Crap!! You died. GAME OVER.", fg=colors.player_die)  # type: ignore


class KeyDownAction(BaseGameAction):
    input_event: tcod.event.Event | None

    def __init__(self, store: GameStore | None = None, handler: SubLoopHandler | None = None, input_event: tcod.event.KeyboardEvent | None = None) -> None:
        super().__init__(store, handler)
        self.input_event = input_event

    def perform(self) -> None:
        if isinstance(self.input_event, tcod.event.KeyboardEvent):
            key_sim = self.input_event.sym if self.input_event else None
            destination = (0, 0)
            action = EntityMoveAction  # Default action

            if self.store and self.store.portfolio.player and key_sim is not None:  # type: ignore | The store for this action must be GameStore.
                if self.store.portfolio.player.location:  # type: ignore | The store for this action must be GameStore.
                    destination = (self.store.portfolio.player.location.x, self.store.portfolio.player.location.y) # type: ignore | The store for this action must be GameStore.

                # Parse movement keys
                match key_sim:
                    # Move Actions
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
                    
                    # Pickup Action
                    case tcod.event.KeySym.SPACE:
                        # Pickup Action
                        destination = self.store.portfolio.player.location.to_tuple  # type: ignore | The store for this action must be GameStore.
                        action = EntityPickupAction

                if destination != (0,0):      
                    self.handler.send(action(store=self.store, handler=self.handler, entity=self.store.portfolio.player,  # type: ignore | The store for this action must be GameStore.
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


player_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    entitywait, entityattack,
    ('inputevent', KeyDownAction()),
}



