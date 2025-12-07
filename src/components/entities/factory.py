#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from src.components.entities.library import *
from components.entities import attributes, ai


PLAYER = Charactor(name="Player", char="@", color=(255, 255, 255),
                   physical=attributes.PhysicalStats(max_hp=30, constitution=14),
                   combat=attributes.CombatStats(defense=2, attack_power=5))
ORC = AICharactor(name="Orc", char="o", color=(63, 127, 63),
                  ai_cls=None, 
                  physical=attributes.PhysicalStats(max_hp=10, constitution=12),
                  combat=attributes.CombatStats(defense=0, attack_power=3))
TROLL = AICharactor(name="Troll", char="T", color=(0, 127, 0), 
                    ai_cls=None,
                    physical=attributes.PhysicalStats(max_hp=16, constitution=12),
                    combat=attributes.CombatStats(defense=1, attack_power=4))


def spawn(original: BaseEntity, location: MapCoords):
    """Spawn a copy of this entity at the given location."""
    clone = deepcopy(original)
    clone.location = location
    return clone
    