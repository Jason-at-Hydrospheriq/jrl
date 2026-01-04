#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from type_protocols import *

from core_components.maps.tiles.base import TileCoordinate

@runtime_checkable
class EntityActionObject(Protocol):
    """The EntityActionObject Protocol is a mixin class that has an 'entity' attribute."""
    store: StatefulObject | None
    transformer: Any | None
    entity: StatefulObject | None

@runtime_checkable
class EntityDestinationObject(Protocol):
    """The EntityDestinationObject Protocol is a mixin class that has a 'destination' attribute."""
    store: StatefulObject | None
    transformer: Any | None
    entity: StatefulObject | None
    destination: TileCoordinate | None

@runtime_checkable
class EntityTargetObject(Protocol):
    """The EntityTargetObject Protocol is a mixin class that has a 'target' attribute."""
    store: StatefulObject | None
    transformer: Any | None
    entity: StatefulObject | None
    target: StatefulObject | None