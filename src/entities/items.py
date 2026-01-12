#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Tuple, TYPE_CHECKING

from baseclasses import BaseGameAction, BaseGameSubState, BaseItem, EntityRenderOrder
from entities.actors import Character
from game_types import TileCoordinate

if TYPE_CHECKING:
    from store import GameStore


class ConsumableItem(BaseItem):
    """A Consumable Item is any game object that can be consumed by a Character. 
    It has a 'spawn' substate that is an instance of BaseGameSubState that manages its 
    spawning states. A Consumable Entity can be used up and removed from the game."""

    _remaining_uses: int = 1
    _max_uses: int = 1
    _action: BaseGameAction | None = None
    _substates_manifest = (
        ("spawn", BaseGameSubState)),

    def __init__(self, store: GameStore | None = None, owner: Character | None = None,
                 location: TileCoordinate | None = None, *, name: str = "<Unnamed>",
                 symbol: str = ' ', color: Tuple[int, int, int]) -> None:
        super().__init__(store, owner, location, name=name, symbol=symbol, color=color)
        self.blocks_movement = False
        self.is_invulnerable = True
        self.render_order = EntityRenderOrder.ITEM
        
    @property
    def remaining_uses(self) -> int:
        return self._remaining_uses

    def use(self) -> None:
        raise NotImplementedError("The 'use' method must be implemented by subclasses of ConsumableEntity.")
    

class HealingPotion(ConsumableItem):
    """A Healing Potion is a Consumable Item that restores health to a Character when used."""

    _healing_amount: int = 20

    def use(self) -> None:
        if isinstance(self.owner, Character):
            if self.owner and not self.owner.health.is_unconscious():
                self.owner.heal(self._healing_amount)
                self._remaining_uses -= 1
                self.store.log.add(f"{self.owner.name} uses {self.name} and is feeling a bit better.")  # type: ignore | Assume store is GameStore
                
                if self._remaining_uses <= 0:
                    # Remove the potion from the game
                    if self.store and self in self.store.portfolio.entities:  # type: ignore | Assume store is GameStore
                        self.store.portfolio.entities.remove(self)  # type: ignore
                self.owner.update()
                self.update()
