#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from components.base import BaseComponent


class PhysicalStats(BaseComponent):
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
    

class MentalStats(BaseComponent):
    intelligence: int
    willpower: int
    max_psyp: int
    
    def __init__(self, intelligence: int, willpower: int, max_psyp: int) -> None:
        self.intelligence = intelligence
        self.willpower = willpower
        self.max_psyp = max_psyp
        self._psyp = max_psyp

    @property
    def psyp(self) -> int:
        return self._psyp
    
    @psyp.setter
    def psyp(self, value: int) -> None:
        self._psyp = max(0, min(value, self.max_psyp))

    def is_conscious(self) -> bool:
        return self.psyp > 0
    

class CombatStats(BaseComponent):
    attack_power: int
    defense: int

    def __init__(self, attack_power: int, defense: int) -> None:
        self.attack_power = attack_power
        self.defense = defense