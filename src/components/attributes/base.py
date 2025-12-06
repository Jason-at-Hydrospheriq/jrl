#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.resources.entities import BaseEntity, PhysicalObject, Charactor, AICharactor
    from engine import Engine


class BaseComponent:
    entity: BaseEntity | PhysicalObject | Charactor | AICharactor

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine
    