#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Protocol, runtime_checkable
from transitions import Machine


@runtime_checkable
class StatefulObject(Protocol):
    """The StatefulObject Protocol is a mixin class that has a 'machine' attribute."""
    machine: Machine # Has a state machine that defines states and transitions.


@runtime_checkable
class StoredStateObject(Protocol):
    """The StoredStateObject Protocol is a mixin class that has a 'store' attribute. It is used to refer to a StatefulObject instance for context."""
    store: StatefulObject | None 




    
