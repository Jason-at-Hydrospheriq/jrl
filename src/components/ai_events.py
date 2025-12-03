#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Protocol
import numpy as np

if TYPE_CHECKING:
    from entities import AICharactor, Charactor


class AIEvent(Protocol):

    def message(self) -> str:
        ...


class AIEventNone:
    def __init__(self, entity: AICharactor) -> None:
        self.entity = entity
        self.target = None
        self.location = None

    def message(self) -> str:
        return f"{self.entity.name} does nothing."

class AIEventMove:
    def __init__(self, entity: AICharactor, location: np.ndarray) -> None:
        self.entity = entity
        self.target = None
        self.location = location

    def message(self) -> str:
        return f"{self.entity.name} moves to {self.location}."

class AIEventMeleeAttack:
    def __init__(self, entity: AICharactor, target: Charactor) -> None:
        self.entity = entity
        self.target = target
        self.location = None

    def message(self) -> str:
        return f"{self.entity.name} attacks {self.target.name}!"
        