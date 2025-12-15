#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core_components.entities.library import BaseEntity, Charactor, AICharactor


class BaseStats:
    entity: BaseEntity | Charactor | AICharactor


class PhysicalStats(BaseStats):
    constitution: int
    max_hp: int

    def __init__(self, constitution: int, max_hp: int) -> None:
        self.constitution = constitution
        self.max_hp = max_hp
        self._hp = max_hp

    @property
    def hp(self) -> int:
        return self._hp
    
    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
    
    def is_destroyed(self) -> bool:
        return self.hp < 1
    

class MentalStats(BaseStats):
    intelligence: int
    willpower: int
    max_mp: int
    
    def __init__(self, intelligence: int, max_mp: int) -> None:
        self.intelligence = intelligence
        self.max_mp = max_mp
        self._mp = max_mp

    @property
    def mp(self) -> int:
        return self._mp
    
    @mp.setter
    def mp(self, value: int) -> None:
        self._mp = max(0, min(value, self.max_mp))

    def is_conscious(self) -> bool:
        return self.mp > 0
    

class CombatStats(BaseStats):
    attack_power: int
    defense: int

    def __init__(self, attack_power: int, defense: int) -> None:
        self.attack_power = attack_power
        self.defense = defense