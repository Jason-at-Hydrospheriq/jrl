#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy

from core_components.entities.library import *
from core_components.entities import attributes, ai
from core_components.tiles.base import TileCoordinate

PLAYER = Charactor(name="Player", symbol="@", color=(255, 255, 255),
                   physical=attributes.PhysicalStats(max_hp=30, constitution=14),
                   combat=attributes.CombatStats(defense=2, attack_power=5))
ORC = AICharactor(name="Orc", symbol="o", color=(63, 127, 63),
                  ai_cls=None, 
                  physical=attributes.PhysicalStats(max_hp=10, constitution=12),
                  combat=attributes.CombatStats(defense=0, attack_power=3))
TROLL = AICharactor(name="Troll", symbol="T", color=(0, 127, 0), 
                    ai_cls=None,
                    physical=attributes.PhysicalStats(max_hp=16, constitution=12),
                    combat=attributes.CombatStats(defense=1, attack_power=4))


def spawn(original: BaseEntity, location: TileCoordinate) -> BaseEntity:
    """Spawn a copy of this entity at the given location."""
    clone = deepcopy(original)
    clone.location = location
    return clone
    